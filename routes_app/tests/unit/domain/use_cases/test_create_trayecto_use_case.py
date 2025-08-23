from routes_app.domain.use_cases.create_trayecto_use_case import CreateTrayectoUseCase

def test_create_trayecto_persists_in_repo(memory_repo, trayecto):
    uc = CreateTrayectoUseCase(repository=memory_repo)
    t = trayecto
    saved = uc.execute(t)
    assert saved == t
    # verificación por lectura directa del repo en memoria
    assert memory_repo.get(t.id) is not None