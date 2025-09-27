import httpx
import os
from datetime import datetime, timezone
from uuid import uuid4

from src.domain.models.credit_card import CreditCard, CreditCardStatus, CreditCardIssuer
from src.domain.models.credit_card_creation_request import CreditCardCreationRequest
from src.domain.ports.credit_card_repository_port import CreditCardRepositoryPort
from src.domain.ports.verification_publisher_port import VerificationPublisherPort
from src.errors import CardAlreadyExistsError, ServiceCommunicationError, CardExpiredError, MalformedRequestError

class CreateCreditCardUseCase:
    def __init__(
        self,
        repository: CreditCardRepositoryPort,
        publisher: VerificationPublisherPort,
    ):
        self.repository = repository
        self.publisher = publisher
        self.true_native_url = os.getenv("TRUENATIVE_SERVICE_URL")
        self.secret_token = os.getenv("TRUENATIVE_SECRET_TOKEN")

    def _validate_card_not_expired(self, expiration_date: str):
        try:
            exp_year, exp_month = int(f"20{expiration_date[:2]}"), int(expiration_date[3:])
            now = datetime.utcnow()
            # The card is valid until the last day of its expiration month
            if now.year > exp_year or (now.year == exp_year and now.month > exp_month):
                raise CardExpiredError()
        except (ValueError, IndexError):
            raise MalformedRequestError("El formato de la fecha de expiración es inválido.")

    def execute(self, user_id: str, request: CreditCardCreationRequest, user_email: str) -> CreditCard:
        # 1. Validaciones de negocio
        self._validate_card_not_expired(request.expirationDate)
        
        last_four = request.cardNumber[-4:]
        if self.repository.find_by_last_four_digits(user_id, last_four):
            raise CardAlreadyExistsError()

        # 2. Comunicación con TrueNative
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    f"{self.true_native_url}/native/cards",
                    headers={"Authorization": f"Bearer {self.secret_token}"},
                    json={
                        "card": request.model_dump(),
                        "transactionIdentifier": str(uuid4())
                    }
                )
                if response.status_code >= 400:
                   raise ServiceCommunicationError(f"TrueNative respondió con error {response.status_code}: {response.text}")
                true_native_data = response.json()
        except httpx.RequestError as e:
            raise ServiceCommunicationError(f"No se pudo conectar con TrueNative: {e}")

        # 3. Creación y persistencia de la entidad
        now = datetime.now(timezone.utc)
        new_card = CreditCard(
            id=str(uuid4()),
            token=true_native_data["token"],
            userId=user_id,
            lastFourDigits=last_four,
            ruv=true_native_data["RUV"],
            issuer=CreditCardIssuer(true_native_data.get("issuer", "UNKNOWN")),
            status=CreditCardStatus.PENDING_VERIFICATION,
            createdAt=now,
            updatedAt=now,
        )
        saved_card = self.repository.save(new_card)

        # 4. Publicación del evento para el polling asíncrono
        self.publisher.publish_for_polling(card_id=saved_card.id, ruv=saved_card.ruv, user_email=user_email)

        return saved_card