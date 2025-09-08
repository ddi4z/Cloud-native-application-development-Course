from pydantic import BaseModel, Field
from typing import List, Optional

# Modelos de inputs recibidos por la app
class RouteOrigin(BaseModel):
    """Sub-modelo para el origen del trayecto en input recibido."""
    airportCode: str
    country: str

class RouteDestiny(BaseModel):
    """Sub-modelo para el destino del trayecto en input recibido."""
    airportCode: str
    country: str

class PostCreationRequest(BaseModel):
    "Modelo de input recibido a la hora de crear un post."
    flightId: str
    expireAt: str
    plannedStartDate: str
    plannedEndDate: str
    origin: RouteOrigin
    destiny: RouteDestiny
    bagcost: int







# Modelos de datos internos (Respuestas de otros servicios)
class User(BaseModel):
    """Modelo resumido para la respuesta del servicio de usuarios."""
    id: str
    username: str

class Post(BaseModel):
    """Modelo resumido para la respuesta del servicio de publicaciones."""
    id: str
    routeId: str
    userId: str
    expireAt: str
    createdAt: str

class Route(BaseModel):
    """Modelo completo para la respuesta del servicio de trayectos."""
    id: str
    flightId: str
    sourceAirportCode: str
    sourceCountry: str
    destinyAirportCode: str
    destinyCountry: str
    bagCost: int
    plannedStartDate: str
    plannedEndDate: str
    createdAt: str

class Offer(BaseModel):
    """Modelo resumido para la respuesta del servicio de ofertas."""
    id: str
    userId: str
    description: str
    size: str
    fragile: bool
    offer: int
    createdAt: str

class OfferWithScore(Offer):
    """Modelo interno que añade el campo 'score' a una oferta."""
    score: Optional[float] = None










# Modelos de la respuesta de la API (estructura de salida)
class RouteDetails(BaseModel):
    """Sub-modelo para los detalles del trayecto en la respuesta final."""
    id: str
    createdAt: str

class PublicationResponseData(BaseModel):
    """Modelo para el objeto 'data' en la respuesta final."""
    id: str
    userId: str
    createdAt: str
    expireAt: str
    route: RouteDetails

class PublicationResponse(BaseModel):
    """Modelo principal que encapsula toda la respuesta final."""
    data: PublicationResponseData
    msg: str













class RouteOrigin(BaseModel):
    """Sub-modelo para el origen del trayecto en la respuesta final."""
    airportCode: str
    country: str

class RouteDestiny(BaseModel):
    """Sub-modelo para el destino del trayecto en la respuesta final."""
    airportCode: str
    country: str

class OfferDetails(BaseModel):
    """Sub-modelo para los detalles de la oferta en la respuesta final."""
    id: str
    userId: str
    description: str
    size: str
    fragile: bool
    offer: int
    score: Optional[float] = None
    createdAt: str

