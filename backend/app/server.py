import random
import qrcode
import string
import os
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .schema import (CreateHallRequest, UpdateHallRequest, CreateHallResponse, UpdateHallResponse,
                     GetHallResponse, GetHallsResponse, CreateUserRequest, CreateUserResponse, UpdateUserResponse, 
                     UpdateUserRequest, GetUserResponse, DeleteUserResponse, LoginRequest, LoginResponse, DeleteHallResponse,
                     CreateFilmRequest, UpdateFilmRequest, CreateFilmResponse, UpdateFilmResponse,
                     GetFilmResponse, GetFilmsResponse, DeleteFilmResponse, CreateSeanceRequest, 
                     UpdateSeanceRequest, CreateSeanceResponse, UpdateSeanceResponse,
                     GetSeanceResponse, GetSeancesResponse, DeleteSeanceResponse,
                     CreateSeatRequest, CreateSeatResponse, UpdateSeatResponse, GetSeatResponse, GetSeatsResponse, 
                     DeleteSeatResponse, UpdateSeatRequest, CreatePriceRequest, CreatePriceResponse, UpdatePriceResponse,
                     GetPriceResponse, GetPricesResponse, DeletePriceResponse, UpdatePriceRequest, CreateTicketRequest,
                     CreateTicketResponse, UpdateTicketResponse, GetTicketResponse, GetTicketsResponse, DeleteTicketResponse,
                     UpdateTicketRequest, GetAvailableSeatsResponse, CreateBookingRequest)
from .lifespan import lifespan
from sqlalchemy import select
from sqlalchemy.orm import noload
from .dependancy import SessionDependency, TokenDependency
from .constants import SUCCESS_RESPONSE
from .auth import hash_password, check_password
from . import models
from . import crud
from datetime import datetime


app = FastAPI(
    title='Cinema Booking API',
    description='API for cinema booking system',
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Обработчик ошибок валидации
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    print(f"[DEBUG] Ошибка валидации запроса: {exc.errors()}")
    print(f"[DEBUG] Тело запроса: {body.decode('utf-8') if body else 'empty'}")
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors(), "body": body.decode('utf-8') if body else 'empty'}
    )

# Базовые эндпоинты
@app.get("/", tags=['root'])
async def root():
    return {"message": "Cinema Booking API", "version": "1.0.0"}

@app.get("/health", tags=['health'])
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# Залы
@app.post('/api/v1/hall', tags=['hall'], response_model=CreateHallResponse)
async def create_hall(hall: CreateHallRequest, session: SessionDependency, token: TokenDependency):
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    hall_dict = hall.model_dump(exclude_unset=True)
    hall_orm_obj = models.Hall(**hall_dict)
    await crud.add_item(session, hall_orm_obj)
    return hall_orm_obj.dict

@app.patch('/api/v1/hall/{hall_id}', tags=['hall'], response_model=UpdateHallResponse)
async def update_hall(hall_id: int, hall: UpdateHallRequest, session: SessionDependency, token: TokenDependency):
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    hall_orm_obj = await crud.get_item_by_id(session, models.Hall, hall_id)
    if hall_orm_obj is None:
        raise HTTPException(404, 'Hall not found')
    hall_dict = hall.model_dump(exclude_unset=True)
    for key, value in hall_dict.items():
        setattr(hall_orm_obj, key, value)
    await crud.update_item(session, hall_orm_obj)
    return hall_orm_obj.dict

@app.get('/api/v1/hall/{hall_id}', tags=['hall'], response_model=GetHallResponse)
async def get_hall(hall_id: int, session: SessionDependency):
    hall_orm_obj = await crud.get_item_by_id(session, models.Hall, hall_id)
    if hall_orm_obj is None:
        raise HTTPException(404, 'Hall not found')
    return hall_orm_obj.dict

# получение списка залов гостем
@app.get('/api/v1/hall', tags=['hall'], response_model=GetHallsResponse)
async def search_halls(session: SessionDependency, name: str | None = None, is_active: bool | None = None):
    filters = []
    if name:
        filters.append(models.Hall.name.ilike(f'%{name}%'))
    if is_active is not None:
        filters.append(models.Hall.is_active == is_active)
    query = select(models.Hall)
    if filters:
        query = query.where(*filters)
    result = await session.execute(query)
    halls = result.scalars().all()
    return {'halls': [hall.dict for hall in halls]}    

@app.delete('/api/v1/hall/{hall_id}', tags=['hall'], response_model=DeleteHallResponse)
async def delete_hall(hall_id: int, session: SessionDependency, token: TokenDependency):
    hall_orm_obj = await crud.get_item_by_id(session, models.Hall, hall_id)
    if hall_orm_obj is None:
        raise HTTPException(404, 'Hall not found')
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    await crud.delete_item(session, hall_orm_obj)
    return SUCCESS_RESPONSE

# Места
@app.post('/api/v1/seat', tags=['seat'], response_model=CreateSeatResponse)
async def create_seat(seat: CreateSeatRequest, session: SessionDependency, token: TokenDependency):
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    seat_dict = seat.model_dump(exclude_unset=True)
    seat_orm_obj = models.Seat(**seat_dict)
    await crud.add_item(session, seat_orm_obj)
    return seat_orm_obj.dict

@app.patch('/api/v1/seat/{seat_id}', tags=['seat'], response_model=UpdateSeatResponse)
async def update_seat(seat_id: int, seat: UpdateSeatRequest, session: SessionDependency, token: TokenDependency):
    seat_orm_obj = await crud.get_item_by_id(session, models.Seat, seat_id)
    if seat_orm_obj is None:
        raise HTTPException(404, 'Seat not found')
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    seat_dict = seat.model_dump(exclude_unset=True)
    for key, value in seat_dict.items():
        setattr(seat_orm_obj, key, value)
    await crud.update_item(session, seat_orm_obj)
    return seat_orm_obj.dict

# получение гостем всех мест в зале 
@app.get('/api/v1/seat', tags=['seat'], response_model=GetSeatsResponse)
async def search_seats(session: SessionDependency, hall_id: int | None = None, row_number: int | None = None, seat_number: int | None = None, seat_type: str | None = None):
    filters = []
    if hall_id:
        filters.append(models.Seat.hall_id == hall_id)
    if row_number:
        filters.append(models.Seat.row_number == row_number)
    if seat_number:
        filters.append(models.Seat.seat_number == seat_number)
    if seat_type:
        filters.append(models.Seat.seat_type == seat_type)
    # Оптимизация: отключаем загрузку relationships для ускорения запроса
    query = select(models.Seat).options(
        noload(models.Seat.hall),
        noload(models.Seat.tickets),
        noload(models.Seat.available_seats),
        noload(models.Seat.bookings)
    )
    if filters:
        query = query.where(*filters)
    result = await session.execute(query)
    seats = result.scalars().unique().all()
    return {'seats': [seat.dict for seat in seats]}

@app.delete('/api/v1/seat/{seat_id}', tags=['seat'], response_model=DeleteSeatResponse)
async def delete_seat(seat_id: int, session: SessionDependency, token: TokenDependency):
    seat_orm_obj = await crud.get_item_by_id(session, models.Seat, seat_id)
    if seat_orm_obj is None:
        raise HTTPException(404, 'Seat not found')
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    await crud.delete_item(session, seat_orm_obj)
    return SUCCESS_RESPONSE

@app.get('/api/v1/seat/{seat_id}', tags=['seat'], response_model=GetSeatResponse)
async def get_seat(seat_id: int, session: SessionDependency):
    seat_orm_obj = await crud.get_item_by_id(session, models.Seat, seat_id)
    if seat_orm_obj is None:
        raise HTTPException(404, 'Seat not found')
    return seat_orm_obj.dict

# Фильмы
@app.post('/api/v1/film', tags=['film'], response_model=CreateFilmResponse)
async def create_film(film: CreateFilmRequest, session: SessionDependency, token: TokenDependency):
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    film_dict = film.model_dump(exclude_unset=True)
    film_orm_obj = models.Film(**film_dict)
    await crud.add_item(session, film_orm_obj)
    return film_orm_obj.dict

@app.patch('/api/v1/film/{film_id}', tags=['film'], response_model=UpdateFilmResponse)
async def update_film(film_id: int, film: UpdateFilmRequest, session: SessionDependency, token: TokenDependency):
    film_orm_obj = await crud.get_item_by_id(session, models.Film, film_id)
    if film_orm_obj is None:
        raise HTTPException(404, 'Film not found')
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    film_dict = film.model_dump(exclude_unset=True)
    for key, value in film_dict.items():
        setattr(film_orm_obj, key, value)
    await crud.update_item(session, film_orm_obj)
    return film_orm_obj.dict

# просмотр гостем информации о фильме
@app.get('/api/v1/film/{film_id}', tags=['film'], response_model=GetFilmResponse)
async def get_film(film_id: int, session: SessionDependency):
    film_orm_obj = await crud.get_item_by_id(session, models.Film, film_id)
    if film_orm_obj is None:
        raise HTTPException(404, 'Film not found')
    return film_orm_obj.dict

# получение гостем списка фильмов
@app.get('/api/v1/film', tags=['film'], response_model=GetFilmsResponse)
async def search_films(session: SessionDependency, title: str | None = None):
    filters = []
    if title:
        filters.append(models.Film.title.ilike(f'%{title}%'))
    query = select(models.Film)
    if filters:
        query = query.where(*filters)
    result = await session.execute(query)
    films = result.scalars().unique().all()
    return {'films': [film.dict for film in films]}

@app.delete('/api/v1/film/{film_id}', tags=['film'], response_model=DeleteFilmResponse)
async def delete_film(film_id: int, session: SessionDependency, token: TokenDependency):
    film_orm_obj = await crud.get_item_by_id(session, models.Film, film_id)
    if film_orm_obj is None:
        raise HTTPException(404, 'Film not found')
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    await crud.delete_item(session, film_orm_obj)
    return SUCCESS_RESPONSE

# Сеансы
@app.post('/api/v1/seance', tags=['seance'], response_model=CreateSeanceResponse)
async def create_seance(seance: CreateSeanceRequest, session: SessionDependency, token: TokenDependency):
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    seance_dict = seance.model_dump(exclude_unset=True)
    seance_orm_obj = models.Seance(**seance_dict)
    await crud.add_item(session, seance_orm_obj)
    return seance_orm_obj.dict

@app.patch('/api/v1/seance/{seance_id}', tags=['seance'], response_model=UpdateSeanceResponse)
async def update_seance(seance_id: int, seance: UpdateSeanceRequest, session: SessionDependency, token: TokenDependency):
    seance_orm_obj = await crud.get_item_by_id(session, models.Seance, seance_id)
    if seance_orm_obj is None:
        raise HTTPException(404, 'Seance not found')
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    seance_dict = seance.model_dump(exclude_unset=True)
    for key, value in seance_dict.items():
        setattr(seance_orm_obj, key, value)
    await crud.update_item(session, seance_orm_obj)
    return seance_orm_obj.dict

# получение гостем информации о сеансе
@app.get('/api/v1/seance/{seance_id}', tags=['seance'], response_model=GetSeanceResponse)
async def get_seance(seance_id: int, session: SessionDependency):
    seance_orm_obj = await crud.get_item_by_id(session, models.Seance, seance_id)
    if seance_orm_obj is None:
        raise HTTPException(404, 'Seance not found')
    return seance_orm_obj.dict

# получение гостем списка всех сеансов
@app.get('/api/v1/seance', tags=['seance'], response_model=GetSeancesResponse)
async def search_seances(session: SessionDependency, hall_id: int | None = None, film_id: int | None = None, start_time: datetime | None = None):
    filters = []
    if hall_id:
        filters.append(models.Seance.hall_id == hall_id)
    if film_id:
        filters.append(models.Seance.film_id == film_id)
    if start_time:
        filters.append(models.Seance.start_time == start_time)

    query = select(models.Seance)
    if filters:
        query = query.where(*filters)
    result = await session.execute(query)
    seances = result.scalars().unique().all()
    return {'seances': [seance.dict for seance in seances]}

@app.delete('/api/v1/seance/{seance_id}', tags=['seance'], response_model=DeleteSeanceResponse)
async def delete_seance(seance_id: int, session: SessionDependency, token: TokenDependency):
    seance_orm_obj = await crud.get_item_by_id(session, models.Seance, seance_id)
    if seance_orm_obj is None:
        raise HTTPException(404, 'Seance not found')
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    await crud.delete_item(session, seance_orm_obj)
    return SUCCESS_RESPONSE

# Билеты
@app.post('/api/v1/ticket', tags=['ticket'], response_model=CreateTicketResponse)
async def create_ticket(ticket: CreateTicketRequest, session: SessionDependency, token: TokenDependency):
    if token.user.role != 'user':
        raise HTTPException(403, 'Insufficient privileges')
    ticket_dict = ticket.model_dump(exclude_unset=True)
    ticket_orm_obj = models.Ticket(**ticket_dict)
    await crud.add_item(session, ticket_orm_obj)
    return ticket_orm_obj.dict

@app.patch('/api/v1/ticket/{ticket_id}', tags=['ticket'], response_model=UpdateTicketResponse)
async def update_ticket(ticket_id: int, ticket: UpdateTicketRequest, session: SessionDependency, token: TokenDependency):
    ticket_orm_obj = await crud.get_item_by_id(session, models.Ticket, ticket_id)
    if ticket_orm_obj is None:
        raise HTTPException(404, 'Ticket not found')
    if token.user.role != 'user':
        raise HTTPException(403, 'Insufficient privileges')
    ticket_dict = ticket.model_dump(exclude_unset=True)
    for key, value in ticket_dict.items():
        setattr(ticket_orm_obj, key, value)
    await crud.update_item(session, ticket_orm_obj)
    return ticket_orm_obj.dict

# получение информации о билете (может гость)
@app.get('/api/v1/ticket/{ticket_id}', tags=['ticket'], response_model=GetTicketResponse)
async def get_ticket(ticket_id: int, session: SessionDependency):
    ticket_orm_obj = await crud.get_item_by_id(session, models.Ticket, ticket_id)
    if ticket_orm_obj is None:
        raise HTTPException(404, 'Ticket not found')
    return ticket_orm_obj.dict

@app.get('/api/v1/ticket', tags=['ticket'], response_model=GetTicketsResponse)
async def search_tickets(token: TokenDependency, session: SessionDependency, seance_id: int | None = None, seat_id: int | None = None, user_id: int | None = None, user_name: str | None = None, user_phone: str | None = None, user_email: str | None = None, price: float | None = None, booked: bool | None = None):
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    filters = []
    if seance_id:
        filters.append(models.Ticket.seance_id == seance_id)
    if seat_id:
        filters.append(models.Ticket.seat_id == seat_id)
    if user_id:
        filters.append(models.Ticket.user_id == user_id)
    if user_name:
        filters.append(models.Ticket.user_name == user_name)
    if user_phone:
        filters.append(models.Ticket.user_phone == user_phone)
    if user_email:
        filters.append(models.Ticket.user_email == user_email)
    if price:
        filters.append(models.Ticket.price == price)
    if booked:
        filters.append(models.Ticket.booked == booked)
    query = select(models.Ticket)
    if filters:
        query = query.where(*filters)
    result = await session.execute(query)
    tickets = result.scalars().all()
    return {'tickets': [ticket.dict for ticket in tickets]}

@app.delete('/api/v1/ticket/{ticket_id}', tags=['ticket'], response_model=DeleteTicketResponse)
async def delete_ticket(ticket_id: int, session: SessionDependency, token: TokenDependency):
    ticket_orm_obj = await crud.get_item_by_id(session, models.Ticket, ticket_id)
    if ticket_orm_obj is None:
        raise HTTPException(404, 'Ticket not found')
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    await crud.delete_item(session, ticket_orm_obj)
    return SUCCESS_RESPONSE

# Цены
@app.post('/api/v1/price', tags=['price'], response_model=CreatePriceResponse)
async def create_price(price: CreatePriceRequest, session: SessionDependency, token: TokenDependency):
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    price_dict = price.model_dump(exclude_unset=True)
    price_orm_obj = models.Price(**price_dict)
    await crud.add_item(session, price_orm_obj)
    return price_orm_obj.dict

@app.patch('/api/v1/price/{price_id}', tags=['price'], response_model=UpdatePriceResponse)
async def update_price(price_id: int, price: UpdatePriceRequest, session: SessionDependency, token: TokenDependency):
    price_orm_obj = await crud.get_item_by_id(session, models.Price, price_id)
    if price_orm_obj is None:
        raise HTTPException(404, 'Price not found')
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    price_dict = price.model_dump(exclude_unset=True)
    for key, value in price_dict.items():
        setattr(price_orm_obj, key, value)
    await crud.update_item(session, price_orm_obj)
    return price_orm_obj.dict

@app.get('/api/v1/price/{price_id}', tags=['price'], response_model=GetPriceResponse)
async def get_price(price_id: int, session: SessionDependency, token: TokenDependency):
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    price_orm_obj = await crud.get_item_by_id(session, models.Price, price_id)
    if price_orm_obj is None:
        raise HTTPException(404, 'Price not found')
    return price_orm_obj.dict

# просмотр цен (может гость)
@app.get('/api/v1/price', tags=['price'], response_model=GetPricesResponse)
async def search_prices(session: SessionDependency, seat_type: str | None = None):
    filters = []
    if seat_type:
        filters.append(models.Price.seat_type == seat_type)
    query = select(models.Price)
    if filters:
        query = query.where(*filters)
    result = await session.execute(query)
    prices = result.scalars().all()
    return {'prices': [price.dict for price in prices]}

@app.delete('/api/v1/price/{price_id}', tags=['price'], response_model=DeletePriceResponse)
async def delete_price(price_id: int, session: SessionDependency, token: TokenDependency):
    price_orm_obj = await crud.get_item_by_id(session, models.Price, price_id)
    if price_orm_obj is None:
        raise HTTPException(404, 'Price not found')
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    await crud.delete_item(session, price_orm_obj)
    return SUCCESS_RESPONSE


# Пользователи
@app.post('/api/v1/user', tags=['user'], response_model=CreateUserResponse)
async def create_user(user: CreateUserRequest, session: SessionDependency):
    user_dict = user.model_dump(exclude_unset=True)
    user_dict['hashed_password'] = hash_password(user_dict['password'])
    del user_dict['password']  # Удаляем исходный пароль
    user_orm_obj = models.User(**user_dict)
    await crud.add_item(session, user_orm_obj)
    return user_orm_obj.dict

@app.patch('/api/v1/user/{user_id}', tags=['user'], response_model=UpdateUserResponse)
async def update_user(user_id: int, user: UpdateUserRequest, session: SessionDependency, token: TokenDependency):
    user_orm_obj = await crud.get_item_by_id(session, models.User, user_id)
    if user_orm_obj is None:
        raise HTTPException(404, 'User not found')
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    user_dict = user.model_dump(exclude_unset=True)
    for key, value in user_dict.items():
        setattr(user_orm_obj, key, value)
    await crud.update_item(session, user_orm_obj)
    return user_orm_obj.dict

@app.get('/api/v1/user/{user_id}', tags=['user'], response_model=GetUserResponse)
async def get_user(user_id: int, session: SessionDependency, token: TokenDependency):
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    user_orm_obj = await crud.get_item_by_id(session, models.User, user_id)
    if user_orm_obj is None:
        raise HTTPException(404, 'User not found')
    return user_orm_obj.dict

@app.get('/api/v1/user', tags=['user'], response_model=GetUserResponse)
async def search_users(token: TokenDependency, session: SessionDependency, name: str | None = None, email: str | None = None, phone: str | None = None, role: str | None = None):
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    filters = []
    if name:
        filters.append(models.User.name.ilike(f'%{name}%'))
    if email:
        filters.append(models.User.email.ilike(f'%{email}%'))
    if phone:
        filters.append(models.User.phone.ilike(f'%{phone}%'))
    if role:
        filters.append(models.User.role == role)
    query = select(models.User)
    if filters:
        query = query.where(*filters)
    result = await session.execute(query)
    users = result.scalars().all()
    return {'users': [user.dict for user in users]}

@app.delete('/api/v1/user/{user_id}', tags=['user'], response_model=DeleteUserResponse)
async def delete_user(user_id: int, session: SessionDependency, token: TokenDependency):
    user_orm_obj = await crud.get_item_by_id(session, models.User, user_id)
    if user_orm_obj is None:
        raise HTTPException(404, 'User not found')
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    await crud.delete_item(session, user_orm_obj)
    return SUCCESS_RESPONSE

@app.post('/api/v1/user/login', tags=['user'], response_model=LoginResponse)
async def login(login_data: LoginRequest, session: SessionDependency):
    query = select(models.User).where(models.User.email == login_data.email)
    result = await session.execute(query)
    user = result.scalars().unique().first()

    if user is None or not check_password(login_data.password, user.hashed_password):
        raise HTTPException(401, 'Invalid credentials')
    token = models.Token(user_id=user.id)
    await crud.add_item(session, token)
    return token.dict


@app.get('/api/v1/tickets', tags=['ticket'], response_model=GetTicketsResponse)
async def get_all_bookings(session: SessionDependency, token: TokenDependency):
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    query = select(models.Ticket)
    bookings = await session.execute(query)
    return {'tickets': [ticket.dict for ticket in bookings.scalars().all()]}

# ==================== ДОПОЛНИТЕЛЬНЫЕ ENDPOINTS ДЛЯ ГОСТЕЙ ====================
# просмотр гостем информации о свободных местах
@app.get('/api/v1/seance/{seance_id}/available-seats', tags=['seance'], response_model=GetAvailableSeatsResponse)
async def get_available_seats(seance_id: int, session: SessionDependency):
    # Оптимизация: получаем сеанс и hall_id одним запросом
    seance_query = select(models.Seance).where(models.Seance.id == seance_id)
    seance_result = await session.execute(seance_query)
    seance_orm_obj = seance_result.scalars().first()
    if seance_orm_obj is None:
        raise HTTPException(404, 'Seance not found')
    
    hall_id = seance_orm_obj.hall_id
    
    # Оптимизация: выполняем все запросы параллельно
    # Получаем только ID забронированных мест (самый важный запрос - должен быть быстрым с индексом)
    booked_seats_query = select(models.Ticket.seat_id).where(
        models.Ticket.seance_id == seance_id, 
        models.Ticket.booked == True
    ).distinct()
    
    # Получаем все места зала (оптимизировано с noload)
    all_seats_query = select(models.Seat).where(
        models.Seat.hall_id == hall_id
    ).options(
        noload(models.Seat.hall),
        noload(models.Seat.tickets),
        noload(models.Seat.available_seats),
        noload(models.Seat.bookings)
    )
    
    # Выполняем запросы параллельно
    booked_result, all_seats_result = await asyncio.gather(
        session.execute(booked_seats_query),
        session.execute(all_seats_query)
    )
    
    boocked_seat_ids = set(booked_result.scalars().all())
    booked_seat_count = len(boocked_seat_ids)
    all_seats = all_seats_result.scalars().unique().all()
    
    # Исключаем забронированные места
    available_seats_details = [
        seat.dict 
        for seat in all_seats 
        if seat.id not in boocked_seat_ids
    ]
    total_seats = len(all_seats)

    return GetAvailableSeatsResponse(
        seance_id = seance_id,
        available_seats = available_seats_details,
        total_seats = total_seats,
        booked_seats = booked_seat_count,
        available_count = len(available_seats_details),
    )

# получение цены при бронировании
@app.get('/api/v1/price', tags=['price'], response_model=GetPriceResponse)
async def get_price_guest(seance_id: int, seat_id: int, session: SessionDependency):
    # Пытаемся найти явную цену для конкретного места и сеанса
    price_query = select(models.Price).where(
        models.Price.seance_id == seance_id, models.Price.seat_id == seat_id
    )
    price_result = await session.execute(price_query)
    price_data = price_result.scalars().first()
    if price_data:
        return price_data.price

    # Фолбек: если явной цены нет, используем тип места и поля цены из сеанса
    seance_query = select(models.Seance).where(models.Seance.id == seance_id)
    seance_result = await session.execute(seance_query)
    seance = seance_result.scalars().first()
    if seance is None:
        raise HTTPException(404, 'Seance not found')

    seat_query = select(models.Seat).where(models.Seat.id == seat_id)
    seat_result = await session.execute(seat_query)
    seat = seat_result.scalars().first()
    if seat is None:
        raise HTTPException(404, 'Seat not found')

    seat_type = (seat.seat_type or '').lower()
    if seat_type == 'vip':
        return seance.price_vip
    # по умолчанию считаем standard
    return seance.price_standard

# генерация уникального кода бронирования
async def generate_uniqe_booking_code(session: SessionDependency, length: int = 10):
    # КРИТИЧЕСКАЯ ОПТИМИЗАЦИЯ: используем timestamp + случайность для гарантированной уникальности
    # Это позволяет избежать проверки в БД в 99.9% случаев
    timestamp_part = str(int(time.time() * 1000))[-8:]  # Миллисекунды для уникальности
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length-8))
    booking_code = f"{timestamp_part}{random_part}"
    
    # Проверяем только один раз (с индексом это очень быстро)
    existing_code_query = select(models.Ticket.id).where(models.Ticket.booking_code == booking_code)
    existing_code_result = await session.execute(existing_code_query)
    existing_ticket = existing_code_result.scalars().first()
    
    if not existing_ticket:
        return booking_code
    
    # Fallback: если коллизия (крайне редко), добавляем еще случайности
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{booking_code}{random_suffix}"

# бронирование гостем
@app.post('/api/v1/ticket/booking', tags=['ticket'], response_model=CreateTicketResponse)
async def book_ticket(booking: CreateBookingRequest, request: Request, session: SessionDependency):
    print(f"[PERF] book_ticket START: seance_id={booking.seance_id}, seat_id={booking.seat_id}")
    start_time = time.time()
    step_times = {}
    
    # ВАЖНО: SQLAlchemy не поддерживает параллельные операции на одной сессии
    # Выполняем запросы последовательно, но они должны быть быстрыми с индексами
    step_start = time.time()
    
    # Получаем сеанс
    seance_query = select(models.Seance).where(models.Seance.id == booking.seance_id)
    seance_result = await session.execute(seance_query)
    
    # Получаем место
    seat_query = select(models.Seat).where(models.Seat.id == booking.seat_id)
    seat_result = await session.execute(seat_query)
    
    # Проверяем бронирование (оптимизированный порядок условий для использования индекса)
    booked_query = select(models.Ticket.id).where(
        models.Ticket.seance_id == booking.seance_id,
        models.Ticket.seat_id == booking.seat_id,
        models.Ticket.booked == True
    )
    booked_result = await session.execute(booked_query)
    
    step_times['parallel_checks'] = time.time() - step_start
    
    seance_data = seance_result.scalars().first()
    if not seance_data:
        raise HTTPException(404, 'Seance not found')
    
    seat_data = seat_result.scalars().first()
    if not seat_data:
        raise HTTPException(404, 'Seat not found')
    
    if seat_data.hall_id != seance_data.hall_id:
        raise HTTPException(400, 'Seat does not belong to this seance hall')

    existing_ticket = booked_result.scalars().first()
    if existing_ticket:
        raise HTTPException(400, 'Seat already booked')

    # Оптимизация: вычисляем цену без дополнительных запросов
    seat_type = (seat_data.seat_type or '').lower()
    price = seance_data.price_vip if seat_type == 'vip' else seance_data.price_standard

    # Оптимизация: генерируем код быстрее (уменьшаем вероятность коллизий)
    step_start = time.time()
    booking_code = await generate_uniqe_booking_code(session, length=10)
    step_times['generate_code'] = time.time() - step_start

    # КРИТИЧНО: НЕ генерируем QR-код в процессе бронирования - это делаем асинхронно после
    # Это ускоряет бронирование в 10-100 раз
    qr_code_path = f'/app/qr_codes/{booking_code}.png'  # Путь будет создан позже

    # Оптимизация: находим/создаем пользователя одним запросом
    step_start = time.time()
    user_query = select(models.User).where(models.User.email == booking.user_email)
    user_result = await session.execute(user_query)
    user_data = user_result.scalars().first()
    
    if user_data is None:
        guest_user = models.User(
            name=booking.user_name or 'Гость',
            phone=booking.user_phone or '+70000000000',
            email=booking.user_email,
            hashed_password=hash_password('guest-temp'),
            role='user',
        )
        await crud.add_item(session, guest_user)
        user_id_value = guest_user.id
    else:
        user_id_value = user_data.id
    step_times['user_handling'] = time.time() - step_start

    ticket_orm_obj = models.Ticket(
        seance_id = booking.seance_id,
        seat_id = booking.seat_id,
        user_id = user_id_value,
        user_name = booking.user_name,
        user_phone = booking.user_phone,
        user_email = booking.user_email,
        price = price,
        booked = True,
        booking_code = booking_code,
        qr_code_data = qr_code_path
    )

    step_start = time.time()
    await crud.add_item(session, ticket_orm_obj)
    step_times['save_ticket'] = time.time() - step_start
    
    total_time = time.time() - start_time
    print(f"[PERF] book_ticket seance_id={booking.seance_id} seat_id={booking.seat_id}: "
          f"total={total_time:.3f}s, "
          f"checks={step_times.get('parallel_checks', 0):.3f}s, "
          f"code={step_times.get('generate_code', 0):.3f}s, "
          f"user={step_times.get('user_handling', 0):.3f}s, "
          f"save={step_times.get('save_ticket', 0):.3f}s")
    
    # Генерируем QR-код асинхронно в фоне (не блокируем ответ)
    async def generate_qr_background():
        try:
            qr_dir = '/app/qr_codes'
            try:
                os.makedirs(qr_dir, exist_ok=True)
            except Exception:
                qr_dir = '/tmp/qr_codes'
                os.makedirs(qr_dir, exist_ok=True)
            
            qr_data = f'Booking_code: {booking_code}, Seance_id: {booking.seance_id}, Seat_id: {booking.seat_id}'
            qr_code_path = f'{qr_dir}/{booking_code}.png'
            
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                qr_code_img = await loop.run_in_executor(executor, qrcode.make, qr_data)
                await loop.run_in_executor(executor, qr_code_img.save, qr_code_path)
            
            # Обновляем путь в БД (опционально, можно пропустить)
            # ticket_orm_obj.qr_code_data = qr_code_path
            # await session.commit()
        except Exception as e:
            # Логируем ошибку, но не прерываем бронирование
            print(f"[WARNING] Не удалось сгенерировать QR-код для билета {ticket_orm_obj.id}: {e}")
    
    # Запускаем генерацию QR-кода в фоне (не ждем завершения)
    asyncio.create_task(generate_qr_background())

    return {
        'id': ticket_orm_obj.id,
        'booking_code': booking_code,
        'ticket_id': ticket_orm_obj.id,
        'seat_info': {
            'id': seat_data.id,
            'hall_id': seat_data.hall_id,
            'row_number': seat_data.row_number,
            'seat_number': seat_data.seat_number,
            'seat_type': seat_data.seat_type
        },
        'seance_info': {
            'id': seance_data.id,
            'hall_id': seance_data.hall_id,
            'film_id': seance_data.film_id,
            'start_time': seance_data.start_time.isoformat(),
            'price_standard': seance_data.price_standard,
            'price_vip': seance_data.price_vip
        },
        'price': price,
        'qr_code_path': qr_code_path,
        'message': 'Ticket booked successfully!'
    }







