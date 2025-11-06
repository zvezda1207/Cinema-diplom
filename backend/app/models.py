from sqlalchemy import Integer, String, DateTime, Float, UUID, ForeignKey, func, Text, Boolean
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from datetime import datetime
import uuid

from . import config 
from .custom_type import ROLE

# КРИТИЧЕСКАЯ ОПТИМИЗАЦИЯ: настраиваем connection pool для производительности
engine = create_async_engine(
    config.PG_DSN,
    pool_size=10,  # Количество соединений в пуле (уменьшено для стабильности)
    max_overflow=5,  # Дополнительные соединения при перегрузке
    pool_pre_ping=False,  # Отключаем pre-ping для скорости (может быть проблемой при разрыве соединений)
    pool_recycle=3600,  # Переиспользование соединений каждый час
    pool_timeout=30,  # Таймаут ожидания соединения из пула
    echo=False,  # Отключаем SQL логирование для производительности
    connect_args={
        "server_settings": {
            "application_name": "cinema_booking",
            "tcp_keepalives_idle": "600",
            "tcp_keepalives_interval": "30",
            "tcp_keepalives_count": "3",
        }
    }
)

Session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase, AsyncAttrs):
    @property
    def id_dict(self):
        return {'id': self.id}
        

class Token(Base):
    __tablename__ = 'tokens'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token: Mapped[uuid.UUID] = mapped_column(UUID, unique=True, server_default=func.gen_random_uuid())
    creation_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    
    user: Mapped['User'] = relationship('User', lazy='joined', back_populates='tokens')

    @property
    def dict(self):
        return {'token': self.token}


class Hall(Base):
    __tablename__ = 'halls'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    rows: Mapped[int] = mapped_column(Integer, nullable=False)
    seats_per_row: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    seats: Mapped[list['Seat']] = relationship('Seat', lazy='joined', back_populates='hall', cascade='all, delete-orphan')
    seances: Mapped[list['Seance']] = relationship('Seance', lazy='joined', back_populates='hall')

    @property
    def dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'rows': self.rows,
            'seats_per_row': self.seats_per_row,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
        }


class Seat(Base):
    __tablename__ = 'seats'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    hall_id: Mapped[int] = mapped_column(Integer, ForeignKey('halls.id'), nullable=False, index=True)
    row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    seat_number: Mapped[int] = mapped_column(Integer, nullable=False)
    seat_type: Mapped[str] = mapped_column(String(20), default='standart')

    hall: Mapped['Hall'] = relationship('Hall', lazy='joined', back_populates='seats')
    tickets: Mapped[list['Ticket']] = relationship('Ticket', lazy='joined', back_populates='seat')
    available_seats: Mapped[list['AvailableSeat']] = relationship('AvailableSeat', lazy='joined', back_populates='seat')
    bookings: Mapped[list['Booking']] = relationship('Booking', lazy='joined', back_populates='seat')

    @property
    def dict(self):
        return {
            'id': self.id,
            'hall_id': self.hall_id,
            'row_number': self.row_number,
            'seat_number': self.seat_number,
            'seat_type': self.seat_type,
        }


class Film(Base):
    __tablename__ = 'films'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Text] = mapped_column(Text)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    poster_url: Mapped[str] = mapped_column(String(500))

    seances: Mapped[list['Seance']] = relationship('Seance', lazy='joined', back_populates='film')

    @property
    def dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'duration': self.duration,
            'poster_url': self.poster_url,
        }

class Seance(Base):
    __tablename__ = 'seances'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    hall_id: Mapped[int] = mapped_column(Integer, ForeignKey('halls.id'), nullable=False)
    film_id: Mapped[int] = mapped_column(Integer, ForeignKey('films.id'), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    price_standard: Mapped[float] = mapped_column(Float, nullable=False)
    price_vip: Mapped[float] = mapped_column(Float, nullable=False)

    film: Mapped['Film'] = relationship('Film', lazy='joined', back_populates='seances')
    hall: Mapped['Hall'] = relationship('Hall', lazy='joined', back_populates='seances')
    tickets: Mapped[list['Ticket']] = relationship('Ticket', lazy='joined', back_populates='seance')
    available_seats: Mapped[list['AvailableSeat']] = relationship('AvailableSeat', lazy='joined', back_populates='seance')
    bookings: Mapped[list['Booking']] = relationship('Booking', lazy='joined', back_populates='seance')

    @property
    def dict(self):
        return {
            'id': self.id,
            'hall_id': self.hall_id,
            'film_id': self.film_id,
            'start_time': self.start_time.isoformat(),
            'price_standard': self.price_standard,
            'price_vip': self.price_vip,
        }


class Ticket(Base):
    __tablename__ = 'tickets'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    seance_id: Mapped[int] = mapped_column(Integer, ForeignKey('seances.id'), nullable=False, index=True)
    seat_id: Mapped[int] = mapped_column(Integer, ForeignKey('seats.id'), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    user_name: Mapped[str] = mapped_column(String(100))
    user_phone: Mapped[str] = mapped_column(String(20))
    user_email: Mapped[str] = mapped_column(String(100))
    booked: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    booking_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    qr_code_data: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    price: Mapped[float] = mapped_column(Float, nullable=False)
        
    user: Mapped['User'] = relationship('User', lazy='joined', back_populates='tickets')
    seance: Mapped['Seance'] = relationship('Seance', lazy='joined', back_populates='tickets')
    seat: Mapped['Seat'] = relationship('Seat', lazy='joined', back_populates='tickets')

    @property
    def dict(self):
        return {
            'id': self.id,
            'seance_id': self.seance_id,
            'seat_id': self.seat_id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_phone': self.user_phone,
            'user_email': self.user_email,
            'booked': self.booked,
            'booking_code': self.booking_code,
            'qr_code_data': self.qr_code_data,
            'created_at': self.created_at.isoformat(),
            'price': self.price,
        }

class Price(Base):
    __tablename__ = 'prices'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    seance_id: Mapped[int] = mapped_column(Integer, ForeignKey('seances.id'), nullable=False)
    seat_id: Mapped[int] = mapped_column(Integer, ForeignKey('seats.id'), nullable=False)
    seat_type: Mapped[str] = mapped_column(String(20), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    # tickets: Mapped[list['Ticket']] = relationship('Ticket', lazy='joined', back_populates='price')

    @property
    def dict(self):
        return {
            'id': self.id,
            'seance_id': self.seance_id,
            'seat_id': self.seat_id,
            'seat_type': self.seat_type,
            'price': self.price,
        }


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[ROLE] = mapped_column(String(20), default='user')
    tokens: Mapped[list['Token']] = relationship('Token', lazy='joined', back_populates='user')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tickets: Mapped[list['Ticket']] = relationship('Ticket', lazy='joined', back_populates='user')
    bookings: Mapped[list['Booking']] = relationship('Booking', lazy='joined', back_populates='user')

   
    @property
    def dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'role': self.role,    
        }

class AvailableSeat(Base):
    __tablename__ = 'available_seats'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    seat_id: Mapped[int] = mapped_column(Integer, ForeignKey('seats.id'), nullable=False, index=True)
    seance_id: Mapped[int] = mapped_column(Integer, ForeignKey('seances.id'), nullable=False, index=True)

    seat: Mapped['Seat'] = relationship('Seat', back_populates='available_seats')
    seance: Mapped['Seance'] = relationship('Seance', back_populates='available_seats')

    @property
    def dict(self):
        return {
        'id': self.id,
        'seat_id': self.seat_id,
        'seance_id': self.seance_id,
        'seat_details': self.seat.dict, 
        }


class Booking(Base):
    __tablename__ = 'bookings'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    seance_id: Mapped[int] = mapped_column(Integer, ForeignKey('seances.id'), nullable=False)
    seat_id: Mapped[int] = mapped_column(Integer, ForeignKey('seats.id'), nullable=False)

    user: Mapped['User'] = relationship('User', lazy='joined', back_populates='bookings')
    seance: Mapped['Seance'] = relationship('Seance', lazy='joined', back_populates='bookings')
    seat: Mapped['Seat'] = relationship('Seat', lazy='joined', back_populates='bookings')


ORM_OBJ = Hall | Seat | Film | Seance | Ticket | User | Price
ORM_CLS = type[Hall] | type[Seat] | type[Film] | type[Seance] | type[Ticket] | type[User] | type[Price]

async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_orm():
    await engine.dispose()
    
