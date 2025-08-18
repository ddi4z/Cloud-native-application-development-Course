from uuid import uuid4
from src.routes_app.domain.models.models import Trayecto

def test_create_and_get(memory_repo, valid_trayecto_data):
    t = Trayecto(**valid_trayecto_data)
    memory_repo.create(t)
    got = memory_repo.get(t.id)
    assert got == t

def test_list_and_count(memory_repo, valid_trayecto_data):
    t1 = Trayecto(**valid_trayecto_data)
    memory_repo.create(t1)
    t2 = Trayecto(**{**valid_trayecto_data, "id": uuid4(), "flightId": "FL124"})
    memory_repo.create(t2)
    items = memory_repo.list()
    assert len(items) == 2

def test_update(memory_repo, valid_trayecto_data):
    t = Trayecto(**valid_trayecto_data)
    memory_repo.create(t)
    t.bagCost = 99
    updated = memory_repo.update(t)
    assert updated.bagCost == 99

def test_delete(memory_repo, trayecto):
    memory_repo.create(trayecto)
    assert memory_repo.delete(trayecto.id) is True
    assert memory_repo.get(trayecto.id) is None

def test_get_by_flight_id(memory_repo, valid_trayecto_data):
    t = Trayecto(**valid_trayecto_data)
    memory_repo.create(t)
    got = memory_repo.get_by_flight_id("FL123")
    assert got.id == t.id

def test_reset(memory_repo, trayecto):
    memory_repo.create(trayecto)
    memory_repo.reset()
    assert memory_repo.list() == []