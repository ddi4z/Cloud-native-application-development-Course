from routes_app.domain.use_cases.delete_trayecto_use_case import DeleteTrayectoUseCase


def test_delete_existing_returns_true(memory_repo, trayecto):
    t = trayecto
    memory_repo.create(t)
    uc = DeleteTrayectoUseCase(repository=memory_repo)
    assert uc.execute(t.id) is True
    assert memory_repo.get(t.id) is None


def test_delete_nonexistent_returns_false(memory_repo):
    from uuid import uuid4

    uc = DeleteTrayectoUseCase(repository=memory_repo)
    assert uc.execute(uuid4()) is False
