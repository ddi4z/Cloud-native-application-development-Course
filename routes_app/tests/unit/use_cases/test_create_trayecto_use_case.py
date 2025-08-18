from src.routes_app.domain.use_cases.create_trayecto_use_case import CreateTrayectoUseCase

def test_create_trayecto_persists_in_repo(repo, make_trayecto):
    uc = CreateTrayectoUseCase(repository=repo)
    t = make_trayecto()
    saved = uc.execute(t)
    assert saved == t
    # verificación por lectura directa del repo en memoria
    assert repo.get(t.id) is not None