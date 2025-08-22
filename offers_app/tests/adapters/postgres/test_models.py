from src.adapters.postgres.models import OfferORM
from src.domain.models.offer import Offer, OfferSize

def test_to_domain(offer_model):
    # Crear ORM desde dominio
    orm_instance: OfferORM = OfferORM.from_domain(offer_model)
    assert isinstance(orm_instance, OfferORM)
    assert orm_instance.description == offer_model.description
    assert orm_instance.size.value == offer_model.size
    assert orm_instance.offer == offer_model.offer

def test_from_domain(offer_model):
    # Convertir de nuevo a dominio
    orm_instance: OfferORM = OfferORM.from_domain(offer_model)
    domain_instance: Offer = orm_instance.to_domain()
    assert domain_instance.size == str(OfferSize(offer_model.size))
    assert domain_instance.description == offer_model.description
    assert domain_instance.offer == offer_model.offer

def test_offer_orm_repr(offer_model):
    # Comprobar la representación: 37
    orm_instance: OfferORM = OfferORM.from_domain(offer_model)
    repr_str = repr(orm_instance)
    assert f"id={orm_instance.id}" in repr_str
    assert f"post_id={orm_instance.post_id}" in repr_str
    assert f"user_id={orm_instance.user_id}" in repr_str
    assert f"size={orm_instance.size}" in repr_str
    assert f"offer={orm_instance.offer}" in repr_str
    assert f"created_at={orm_instance.created_at}" in repr_str
