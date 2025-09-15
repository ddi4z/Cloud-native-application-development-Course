from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from uuid import UUID
from datetime import datetime
    

# User
class User(BaseModel):
    """User domain model."""
    id: str
    username: str
    email: str
    fullName: str
    dni: str
    phoneNumber: str
    status: str


# Post
class Post(BaseModel):
    """Post domain model."""
    id: str
    routeId: str
    userId: str
    expireAt: str # 2025-09-18T02:04:26.637Z
    createdAt: str # 2025-09-18T02:04:26.637Z


class CreatedPost(BaseModel):
    """CreatedPost."""
    routeId: UUID
    userId: datetime
    createdAt: UUID


# Route
class Route(BaseModel):
    """Route domain model."""
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

class CreatedRoute(BaseModel):
    """CreatedRoute."""
    id: str
    createdAt: str




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
    """Received Input from User, passed through HTTP."""
    flightId: str
    expireAt: str
    plannedStartDate: str
    plannedEndDate: str
    origin: RouteOrigin
    destiny: RouteDestiny
    bagCost: int














# Communication with other MSs
    # INPUTS
    # Users
class CreatePost(BaseModel):
    """Modelo resumido para la respuesta del servicio de publicaciones."""
    id: str
    expireAt: str
    userId: str

class RouteCreateInput(BaseModel):
    """Modelo completo para la respuesta del servicio de trayectos."""
    flightId: str
    sourceAirportCode: str
    sourceCountry: str
    destinyAirportCode: str
    destinyCountry: str
    bagCost: int
    plannedStartDate: str
    plannedEndDate: str


    # OUTPUTS
class UserGetResponse(BaseModel):
    """Modelo resumido para la respuesta del servicio de usuarios."""
    id: str
    username: str
    email: EmailStr
    fullName: Optional[str]
    dni: Optional[str]
    phoneNumber: Optional[str]
    status: Optional[str]

    # routes
class RouteGetResponse(BaseModel):
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

class RouteCreateResponse(BaseModel):
    """Modelo completo para la respuesta del servicio de trayectos."""
    id: str
    createdAt: str


    # posts
class Post(BaseModel):
    """Modelo resumido para la respuesta del servicio de publicaciones."""
    id: str
    routeId: str
    userId: str
    expireAt: str
    createdAt: str

class CreatePostResponse(BaseModel):
    """Modelo para la respuesta de creación de post"""
    id: str
    userId: str
    createdAt: str






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
    msg: str = 'Publicación creada exitosamente'