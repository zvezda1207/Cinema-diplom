from pydantic import BaseModel, EmailStr, Field
from typing import Literal
import uuid
from datetime import datetime


class SuccessResponse(BaseModel):
    status: Literal['success']

# Залы
class CreateHallRequest(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    rows: int = Field(gt=0)
    seats_per_row: int = Field(gt=0)

class UpdateHallRequest(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    rows: int = Field(gt=0)
    seats_per_row: int = Field(gt=0)

class CreateHallResponse(BaseModel):
    id: int

class UpdateHallResponse(BaseModel):
    id: int

class GetHallResponse(BaseModel):
    id: int
    name: str
    rows: int
    seats_per_row: int
    is_active: bool
    created_at: str

class GetHallsResponse(BaseModel):
    halls: list[GetHallResponse]

class DeleteHallResponse(SuccessResponse):
    pass

# Пользователи
class BaseUserRequest(BaseModel):
    name: str
    password: str

class CreateUserRequest(BaseModel):
    name: str
    phone: str
    email: str
    password: str

class CreateUserResponse(BaseModel):
    id: int
    
class GetUserResponse(BaseModel):
    id: int
    name: str
    role: str

class UpdateUserResponse(SuccessResponse):
    pass

class UpdateUserRequest(BaseModel):
    name: str | None = Field(min_length=3, max_length=100)
    password: str | None = Field(min_length=8, max_length=100)
    role: str | None = Field(min_length=3, max_length=20)

# Авторизация
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: uuid.UUID

# Фильмы
class CreateFilmRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    duration: int = Field(gt=0, description="Duration in minutes")
    poster_url: str | None = Field(max_length=500)

class CreateFilmResponse(BaseModel):
    id: int

class UpdateFilmRequest(BaseModel):
    title: str | None = Field(min_length=1, max_length=200)
    description: str | None = None
    duration: int | None = Field(gt=0, description="Duration in minutes")
    poster_url: str | None = Field(max_length=500)

class UpdateFilmResponse(BaseModel):
    id: int

class GetFilmResponse(BaseModel):
    id: int
    title: str
    description: str | None
    duration: int
    poster_url: str | None

class GetFilmsResponse(BaseModel):
    films: list[GetFilmResponse]

class DeleteFilmResponse(SuccessResponse):
    pass

# Сеансы
class CreateSeanceRequest(BaseModel):
    hall_id: int
    film_id: int
    start_time: datetime
    price_standard: float
    price_vip: float

class CreateSeanceResponse(BaseModel):
    id: int

class UpdateSeanceRequest(BaseModel):
    hall_id: int | None = None
    film_id: int | None = None
    start_time: datetime | None = None
    price_standard: float | None = None
    price_vip: float | None = None

class UpdateSeanceResponse(BaseModel):
    id: int

class GetSeanceResponse(BaseModel):
    id: int
    hall_id: int
    film_id: int
    start_time: datetime
    price_standard: float | None = None
    price_vip: float | None = None

class GetSeancesResponse(BaseModel):
    seances: list[GetSeanceResponse]

class DeleteSeanceResponse(SuccessResponse):
    pass

# Цены
class CreatePriceRequest(BaseModel):
    seance_id: int
    seat_id: int
    seat_type: str
    price: float

class CreatePriceResponse(BaseModel):
    id: int

class UpdatePriceRequest(BaseModel):
    seat_type: str | None = None
    price: float | None = None

class UpdatePriceResponse(BaseModel):
    id: int

class GetPriceResponse(BaseModel):
    id: int
    seat_type: str
    price: float

class GetPricesResponse(BaseModel):
    prices: list[GetPriceResponse]

class DeletePriceResponse(SuccessResponse):
    pass

# Места
class CreateSeatRequest(BaseModel):
    hall_id: int
    row_number: int
    seat_number: int
    seat_type: str

class CreateSeatResponse(BaseModel):
    id: int

class UpdateSeatRequest(BaseModel):
    hall_id: int | None = None
    row_number: int | None = None
    seat_number: int | None = None
    seat_type: str | None = None

class UpdateSeatResponse(BaseModel):
    id: int

class GetSeatResponse(BaseModel):
    id: int
    hall_id: int
    row_number: int
    seat_number: int
    seat_type: str

class GetSeatsResponse(BaseModel):
    seats: list[GetSeatResponse]

class DeleteSeatResponse(SuccessResponse):
    pass

# свободные места

class CreateAvailableSeatResponse(BaseModel):
    id: int

class GetAvailableSeatsResponse(BaseModel):
    seance_id: int
    available_seats: list[GetSeatResponse]
    total_seats: int
    booked_seats: int
    available_count: int 
    
# бронирования
class CreateBookingRequest(BaseModel):
    seance_id: int
    seat_id: int
    user_name: str
    user_phone: str
    user_email: str
    qr_code_data: str


# Билеты
class CreateTicketRequest(BaseModel):
    seance_id: int
    seat_id: int
    user_id: int
    user_name: str
    user_phone: str
    user_email: str
    price: float

class CreateTicketResponse(BaseModel):
    id: int
    booking_code: str | None = None
    ticket_id: int | None = None
    seat_info: dict | None = None
    seance_info: dict | None = None
    price: float | None = None
    qr_code_path: str | None = None
    message: str | None = None

class UpdateTicketRequest(BaseModel):
    seance_id: int | None = None
    seat_id: int | None = None
    user_id: int | None = None
    user_name: str | None = None
    user_phone: str | None = None
    user_email: str | None = None
    price: float | None = None

class UpdateTicketResponse(BaseModel):
    id: int

class GetTicketResponse(BaseModel):
    id: int
    seance_id: int
    seat_id: int
    user_id: int
    user_name: str
    user_phone: str 
    user_email: str
    price: float
    booked: bool
    booking_code: str
    qr_code_data: str

class GetTicketsResponse(BaseModel):
    tickets: list[GetTicketResponse]

class DeleteTicketResponse(SuccessResponse):
    pass

class DeleteUserResponse(SuccessResponse):
    pass

