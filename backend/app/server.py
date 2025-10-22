import random
import string
from fastapi import FastAPI, HTTPException
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
                     UpdateTicketRequest)
from .lifespan import lifespan
from sqlalchemy import select
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

# Залы
@app.post('api/v1/hall', tags=['hall'], response_model=CreateHallResponse)
async def create_hall(hall: CreateHallRequest, session: SessionDependency, token: TokenDependency):
    hall_dict = hall.model_dump(exclude_unset=True)
    hall_orm_obj = models.Hall(**hall_dict, user_id=token.user_id)
    await crud.add_item(session, hall_orm_obj)
    return hall_orm_obj.dict

@app.patch('api/v1/hall/{hall_id}', tags=['hall'], response_model=UpdateHallResponse)
async def update_hall(hall_id: int, hall: UpdateHallRequest, session: SessionDependency, token: TokenDependency):
    hall_orm_obj = await crud.get_item_by_id(session, models.Hall, hall_id)
    if hall_orm_obj is None:
        raise HTTPException(404, 'Hall not found')
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    hall_dict = hall.model_dump(exclude_unset=True)
    for key, value in hall_dict.items():
        setattr(hall_orm_obj, key, value)
    await crud.update_item(session, hall_orm_obj)
    return hall_orm_obj.dict

@app.get('api/v1/hall/{hall_id}', tags=['hall'], response_model=GetHallResponse)
async def get_hall(hall_id: int, session: SessionDependency):
    hall_orm_obj = await crud.get_item_by_id(session, models.Hall, hall_id)
    if hall_orm_obj is None:
        raise HTTPException(404, 'Hall not found')
    return hall_orm_obj.dict

@app.get('api/v1/hall', tags=['hall'], response_model=GetHallsResponse)
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

@app.delete('api/v1/hall/{hall_id}', tags=['hall'], response_model=DeleteHallResponse)
async def delete_hall(hall_id: int, session: SessionDependency, token: TokenDependency):
    hall_orm_obj = await crud.get_item_by_id(session, models.Hall, hall_id)
    if hall_orm_obj is None:
        raise HTTPException(404, 'Hall not found')
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    await crud.delete_item(session, hall_orm_obj)
    return SUCCESS_RESPONSE

# Места
@app.post('api/v1/seat', tags=['seat'], response_model=CreateSeatResponse)
async def create_seat(seat: CreateSeatRequest, session: SessionDependency, token: TokenDependency):
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    seat_dict = seat.model_dump(exclude_unset=True)
    seat_orm_obj = models.Seat(**seat_dict)
    await crud.add_item(session, seat_orm_obj)
    return seat_orm_obj.dict

@app.patch('api/v1/seat/{seat_id}', tags=['seat'], response_model=UpdateSeatResponse)
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

@app.get('api/v1/seat', tags=['seat'], response_model=GetSeatsResponse)
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
    query = select(models.Seat)
    if filters:
        query = query.where(*filters)
    result = await session.execute(query)
    seats = result.scalars().all()
    return {'seats': [seat.dict for seat in seats]}

@app.delete('api/v1/seat/{seat_id}', tags=['seat'], response_model=DeleteSeatResponse)
async def delete_seat(seat_id: int, session: SessionDependency, token: TokenDependency):
    seat_orm_obj = await crud.get_item_by_id(session, models.Seat, seat_id)
    if seat_orm_obj is None:
        raise HTTPException(404, 'Seat not found')
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    await crud.delete_item(session, seat_orm_obj)
    return SUCCESS_RESPONSE

@app.get('api/v1/seat/{seat_id}', tags=['seat'], response_model=GetSeatResponse)
async def get_seat(seat_id: int, session: SessionDependency):
    seat_orm_obj = await crud.get_item_by_id(session, models.Seat, seat_id)
    if seat_orm_obj is None:
        raise HTTPException(404, 'Seat not found')
    return seat_orm_obj.dict

# Фильмы
@app.post('api/v1/film', tags=['film'], response_model=CreateFilmResponse)
async def create_film(film: CreateFilmRequest, session: SessionDependency, token: TokenDependency):
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    film_dict = film.model_dump(exclude_unset=True)
    film_orm_obj = models.Film(**film_dict)
    await crud.add_item(session, film_orm_obj)
    return film_orm_obj.dict

@app.patch('api/v1/film/{film_id}', tags=['film'], response_model=UpdateFilmResponse)
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

@app.get('api/v1/film/{film_id}', tags=['film'], response_model=GetFilmResponse)
async def get_film(film_id: int, session: SessionDependency):
    film_orm_obj = await crud.get_item_by_id(session, models.Film, film_id)
    if film_orm_obj is None:
        raise HTTPException(404, 'Film not found')
    return film_orm_obj.dict

@app.get('api/v1/film', tags=['film'], response_model=GetFilmsResponse)
async def search_films(session: SessionDependency, title: str | None = None):
    filters = []
    if title:
        filters.append(models.Film.title.ilike(f'%{title}%'))
    query = select(models.Film)
    if filters:
        query = query.where(*filters)
    result = await session.execute(query)
    films = result.scalars().all()
    return {'films': [film.dict for film in films]}

@app.delete('api/v1/film/{film_id}', tags=['film'], response_model=DeleteFilmResponse)
async def delete_film(film_id: int, session: SessionDependency, token: TokenDependency):
    film_orm_obj = await crud.get_item_by_id(session, models.Film, film_id)
    if film_orm_obj is None:
        raise HTTPException(404, 'Film not found')
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    await crud.delete_item(session, film_orm_obj)
    return SUCCESS_RESPONSE

# Сеансы
@app.post('api/v1/seance', tags=['seance'], response_model=CreateSeanceResponse)
async def create_seance(seance: CreateSeanceRequest, session: SessionDependency, token: TokenDependency):
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    seance_dict = seance.model_dump(exclude_unset=True)
    seance_orm_obj = models.Seance(**seance_dict)
    await crud.add_item(session, seance_orm_obj)
    return seance_orm_obj.dict

@app.patch('api/v1/seance/{seance_id}', tags=['seance'], response_model=UpdateSeanceResponse)
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

@app.get('api/v1/seance/{seance_id}', tags=['seance'], response_model=GetSeanceResponse)
async def get_seance(seance_id: int, session: SessionDependency):
    seance_orm_obj = await crud.get_item_by_id(session, models.Seance, seance_id)
    if seance_orm_obj is None:
        raise HTTPException(404, 'Seance not found')
    return seance_orm_obj.dict

@app.get('api/v1/seance', tags=['seance'], response_model=GetSeancesResponse)
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
    seances = result.scalars().all()
    return {'seances': [seance.dict for seance in seances]}

@app.delete('api/v1/seance/{seance_id}', tags=['seance'], response_model=DeleteSeanceResponse)
async def delete_seance(seance_id: int, session: SessionDependency, token: TokenDependency):
    seance_orm_obj = await crud.get_item_by_id(session, models.Seance, seance_id)
    if seance_orm_obj is None:
        raise HTTPException(404, 'Seance not found')
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    await crud.delete_item(session, seance_orm_obj)
    return SUCCESS_RESPONSE

# Билеты
@app.post('api/v1/ticket', tags=['ticket'], response_model=CreateTicketResponse)
async def create_ticket(ticket: CreateTicketRequest, session: SessionDependency, token: TokenDependency):
    if token.user.role != 'user':
        raise HTTPException(403, 'Insufficient privileges')
    ticket_dict = ticket.model_dump(exclude_unset=True)
    ticket_orm_obj = models.Ticket(**ticket_dict)
    await crud.add_item(session, ticket_orm_obj)
    return ticket_orm_obj.dict

@app.patch('api/v1/ticket/{ticket_id}', tags=['ticket'], response_model=UpdateTicketResponse)
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

@app.get('api/v1/ticket/{ticket_id}', tags=['ticket'], response_model=GetTicketResponse)
async def get_ticket(ticket_id: int, session: SessionDependency):
    ticket_orm_obj = await crud.get_item_by_id(session, models.Ticket, ticket_id)
    if ticket_orm_obj is None:
        raise HTTPException(404, 'Ticket not found')
    return ticket_orm_obj.dict

@app.get('api/v1/ticket', tags=['ticket'], response_model=GetTicketsResponse)
async def search_tickets(session: SessionDependency, seance_id: int | None = None, seat_id: int | None = None, user_id: int | None = None, user_name: str | None = None, user_phone: str | None = None, user_email: str | None = None, price: float | None = None, booked: bool | None = None):
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

@app.delete('api/v1/ticket/{ticket_id}', tags=['ticket'], response_model=DeleteTicketResponse)
async def delete_ticket(ticket_id: int, session: SessionDependency, token: TokenDependency):
    ticket_orm_obj = await crud.get_item_by_id(session, models.Ticket, ticket_id)
    if ticket_orm_obj is None:
        raise HTTPException(404, 'Ticket not found')
    if token.user.role != 'user':
        raise HTTPException(403, 'Insufficient privileges')
    await crud.delete_item(session, ticket_orm_obj)
    return SUCCESS_RESPONSE

# Цены
@app.post('api/v1/price', tags=['price'], response_model=CreatePriceResponse)
async def create_price(price: CreatePriceRequest, session: SessionDependency, token: TokenDependency):
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    price_dict = price.model_dump(exclude_unset=True)
    price_orm_obj = models.Price(**price_dict)
    await crud.add_item(session, price_orm_obj)
    return price_orm_obj.dict

@app.patch('api/v1/price/{price_id}', tags=['price'], response_model=UpdatePriceResponse)
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
    
@app.get('api/v1/price/{price_id}', tags=['price'], response_model=GetPriceResponse)
async def get_price(price_id: int, session: SessionDependency):
    price_orm_obj = await crud.get_item_by_id(session, models.Price, price_id)
    if price_orm_obj is None:
        raise HTTPException(404, 'Price not found')
    return price_orm_obj.dict

@app.get('api/v1/price', tags=['price'], response_model=GetPricesResponse)
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

@app.delete('api/v1/price/{price_id}', tags=['price'], response_model=DeletePriceResponse)
async def delete_price(price_id: int, session: SessionDependency, token: TokenDependency):
    price_orm_obj = await crud.get_item_by_id(session, models.Price, price_id)
    if price_orm_obj is None:
        raise HTTPException(404, 'Price not found')
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    await crud.delete_item(session, price_orm_obj)
    return SUCCESS_RESPONSE


# Пользователи
@app.post('api/v1/user', tags=['user'], response_model=CreateUserResponse)
async def create_user(user: CreateUserRequest, session: SessionDependency):
    user_dict = user.model_dump(exclude_unset=True)
    user_dict['password'] = hash_password(user_dict['password'])
    user_orm_obj = models.User(**user_dict)
    await crud.add_item(session, user_orm_obj)
    return user_orm_obj.dict

@app.patch('api/v1/user/{user_id}', tags=['user'], response_model=UpdateUserResponse)
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

@app.get('api/v1/user/{user_id}', tags=['user'], response_model=GetUserResponse)
async def get_user(user_id: int, session: SessionDependency):
    user_orm_obj = await crud.get_item_by_id(session, models.User, user_id)
    if user_orm_obj is None:
        raise HTTPException(404, 'User not found')
    return user_orm_obj.dict

@app.get('api/v1/user', tags=['user'], response_model=GetUserResponse)
async def search_users(session: SessionDependency, name: str | None = None, email: str | None = None, phone: str | None = None, role: str | None = None):
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

@app.delete('api/v1/user/{user_id}', tags=['user'], response_model=DeleteUserResponse)
async def delete_user(user_id: int, session: SessionDependency, token: TokenDependency):
    user_orm_obj = await crud.get_item_by_id(session, models.User, user_id)
    if user_orm_obj is None:
        raise HTTPException(404, 'User not found')
    if token.user.role != 'admin':
        raise HTTPException(403, 'Insufficient privileges')
    await crud.delete_item(session, user_orm_obj)
    return SUCCESS_RESPONSE

@app.post('api/v1/user/login', tags=['user'], response_model=LoginResponse)
async def login(login_data: LoginRequest, session: SessionDependency):
    query = select(models.User).where(models.User.name == login_data.name)
    result = await session.execute(query)
    user = result.scalars().unique().first()

    if user is None or not check_password(login_data.password, user.hashed_password):
        raise HTTPException(401, 'Invalid credentials')
    token = models.Token(user_id=user.id)
    await crud.add_item(session, token)
    return token.dict


# ==================== ДОПОЛНИТЕЛЬНЫЕ ENDPOINTS ДЛЯ ГОСТЕЙ ====================

@app.get('/api/v1/seances/{seance_id}/available-seats')
async def get_available_seats(seance_id: int, session: SessionDependency):
    """Получение доступных мест для сеанса (публичный доступ)"""
    # Получаем сеанс
    seance = await crud.get_item_by_id(session, models.Seance, seance_id)
    
    # Получаем все места в зале
    seats_query = select(models.Seat).where(models.Seat.hall_id == seance.hall_id)
    seats_result = await session.execute(seats_query)
    all_seats = seats_result.scalars().all()
    
    # Получаем забронированные места
    booked_query = select(models.Ticket).where(
        models.Ticket.seance_id == seance_id,
        models.Ticket.booked == True
    )
    booked_result = await session.execute(booked_query)
    booked_tickets = booked_result.scalars().all()
    booked_seat_ids = {ticket.seat_id for ticket in booked_tickets}
    
    # Фильтруем доступные места
    available_seats = [seat.dict for seat in all_seats if seat.id not in booked_seat_ids]
    
    return {
        'seance_id': seance_id,
        'available_seats': available_seats,
        'total_seats': len(all_seats),
        'booked_seats': len(booked_seat_ids),
        'available_count': len(available_seats)
    }

@app.post('/api/v1/book-ticket')
async def book_ticket_guest(
    seance_id: int,
    seat_id: int,
    user_name: str,
    user_phone: str,
    user_email: str,
    session: SessionDependency
):
    """Бронирование билета гостем (публичный доступ)"""

    
    # Проверяем, что сеанс существует
    seance = await crud.get_item_by_id(session, models.Seance, seance_id)
    
    # Проверяем, что место существует и принадлежит залу сеанса
    seat = await crud.get_item_by_id(session, models.Seat, seat_id)
    if seat.hall_id != seance.hall_id:
        raise HTTPException(400, 'Seat does not belong to this seance hall')
    
    # Проверяем, что место не забронировано
    existing_ticket_query = select(models.Ticket).where(
        models.Ticket.seance_id == seance_id,
        models.Ticket.seat_id == seat_id,
        models.Ticket.booked == True
    )
    existing_ticket_result = await session.execute(existing_ticket_query)
    existing_ticket = existing_ticket_result.scalars().first()
    
    if existing_ticket:
        raise HTTPException(400, 'Seat is already booked')
    
    # Определяем цену в зависимости от типа места
    price = seance.price_standard if seat.seat_type == 'standard' else seance.price_vip
    
    # Создаем временного пользователя
    temp_user = models.User(
        name=user_name,
        phone=user_phone,
        email=user_email,
        hashed_password='temp_password',  # Временный пароль
        role='user'
    )
    await crud.add_item(session, temp_user)
    
    # Генерируем код бронирования
    booking_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Создаем билет
    ticket = models.Ticket(
        seance_id=seance_id,
        seat_id=seat_id,
        user_id=temp_user.id,
        user_name=user_name,
        user_phone=user_phone,
        user_email=user_email,
        price=price,
        booked=True,
        booking_code=booking_code,
        qr_code_data=f"BOOKING_{booking_code}"
    )
    await crud.add_item(session, ticket)
    
    return {
        'booking_code': booking_code,
        'ticket_id': ticket.id,
        'seat_info': seat.dict,
        'seance_info': seance.dict,
        'price': price,
        'message': 'Ticket booked successfully!'
    }
