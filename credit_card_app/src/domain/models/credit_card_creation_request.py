from pydantic import BaseModel, Field, field_validator
import re

class CreditCardCreationRequest(BaseModel):
    """Modelo para el cuerpo de la solicitud de creación de tarjeta."""
    cardNumber: str = Field(description="Número de la tarjeta completo y sin espacios")
    cvv: str = Field(description="Número de verificación de la tarjeta")
    expirationDate: str = Field(description="Fecha de expiración en formato YY/MM")
    cardHolderName: str = Field(description="Nombre del propietario grabado en la tarjeta")

    @field_validator('cardNumber')
    @classmethod
    def card_number_must_be_numeric(cls, v):
        if not v.isdigit() or not 13 <= len(v) <= 19:
            raise ValueError('El número de tarjeta debe ser numérico y tener entre 13 y 19 dígitos.')
        return v

    @field_validator('cvv')
    @classmethod
    def cvv_must_be_numeric(cls, v):
        if not v.isdigit() or not 3 <= len(v) <= 4:
            raise ValueError('El CVV debe ser numérico y tener 3 o 4 dígitos.')
        return v

    @field_validator('expirationDate')
    @classmethod
    def expiration_date_format(cls, v):
        import re
        if not re.match(r'^\d{2}/\d{2}$', v):
            raise ValueError('La fecha de expiración debe tener el formato YY/MM.')
        return v

