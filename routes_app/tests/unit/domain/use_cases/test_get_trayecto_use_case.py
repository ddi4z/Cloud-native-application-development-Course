from routes_app.domain.use_cases.get_trayecto_use_case import GetTrayectoUseCase

def test_get_existing_trayecto(memory_repo, trayecto):
    t = trayecto
    memory_repo.create(t)
    uc = GetTrayectoUseCase(repository=memory_repo)
    got = uc.execute(t.id)
    assert got is not None
    assert got.id == t.id

def test_get_nonexistent_trayecto_returns_none(memory_repo):
    from uuid import uuid4
    uc = GetTrayectoUseCase(repository=memory_repo)
    assert uc.execute(uuid4()) is None