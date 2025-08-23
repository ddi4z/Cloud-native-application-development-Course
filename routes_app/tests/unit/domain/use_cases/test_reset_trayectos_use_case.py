from routes_app.domain.use_cases.reset_trayectos_use_case import ResetTrayectosUseCase


def test_reset_clears_all(memory_repo, trayecto):
    memory_repo.create(trayecto)
    memory_repo.create(trayecto)
    uc = ResetTrayectosUseCase(repository=memory_repo)
    uc.execute()
    assert memory_repo.count() == 0
