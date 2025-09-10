from pydantic import BaseModel, Field
from typing import List, Optional


# Inputs received from user: submodels
class RouteOrigin(BaseModel):
    """Sub-modelo para origen de un trayecto en user input"""
    airportCode: str
    country: str

class RouteDestiny(BaseModel):
    """Sub-modelo para origen de un trayecto en user input"""
    airportCode: str
    country: str


# Inputs received from user
class UserInput(BaseModel):
    """Modelo resumido para la respuesta del servicio de usuarios."""
    flightId: str
    expireAt: str
    plannedStartDate: str
    plannedEndDate: str
    origin: RouteOrigin
    destiny: RouteDestiny
    bagCost: int
    





# Communication with other MSs
    # Users
class User(BaseModel):
    """Modelo resumido para la respuesta del servicio de usuarios."""
    id: str
    username: str

    # routes
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

    # posts
class Post(BaseModel):
    """Modelo resumido para la respuesta del servicio de publicaciones."""
    id: str
    routeId: str
    userId: str
    expireAt: str
    createdAt: str


class CreateRoute(BaseModel):
    """"Modelo para la creación de una ruta."""
    flightId: str
    sourceAirportCode: str
    sourceCountry: str
    destinyAirportCode: str
    destinyCountry: str
    bagCost: int
    plannedStartDate: str
    plannedEndDate: str



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