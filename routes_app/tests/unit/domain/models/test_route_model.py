from uuid import UUID
from datetime import datetime, timezone
from src.routes_app.domain.models import Trayecto


def test_trayecto_campos_basicos_y_ids():
    t = Trayecto(
        flightId="AA001",
        sourceAirportCode="BOG",
        sourceCountry="Colombia",
        destinyAirportCode="MIA",
        destinyCountry="USA",
        bagCost=50,
        plannedStartDate=datetime(2030, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        plannedEndDate=datetime(2030, 1, 1, 14, 0, 0, tzinfo=timezone.utc),
    )

    assert isinstance(t.id, UUID)
    assert t.flightId == "AA001"
    assert t.sourceAirportCode == "BOG"
    assert t.destinyAirportCode == "MIA"
    assert t.bagCost == 50
    assert t.plannedStartDate.tzinfo is not None
    assert t.plannedEndDate.tzinfo is not None
    # createdAt/updatedAt se autogeneran en UTC
    assert t.createdAt.tzinfo is not None
    assert t.updatedAt.tzinfo is not None