# from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship
# from datetime import datetime

# Base = declarative_base()


# class Hall(Base):
#     """Модель кинозала"""
#     __tablename__ = "halls"
    
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(100), nullable=False)
#     rows = Column(Integer, nullable=False)
#     seats_per_row = Column(Integer, nullable=False)
#     is_active = Column(Boolean, default=False)  # Открыта ли продажа билетов
#     created_at = Column(DateTime, default=datetime.utcnow)
    
#     # Relationships
#     seats = relationship("Seat", back_populates="hall", cascade="all, delete-orphan")
#     sessions = relationship("Session", back_populates="hall")


# class Seat(Base):
#     """Модель места в зале"""
#     __tablename__ = "seats"
    
#     id = Column(Integer, primary_key=True, index=True)
#     hall_id = Column(Integer, ForeignKey("halls.id"), nullable=False)
#     row_number = Column(Integer, nullable=False)
#     seat_number = Column(Integer, nullable=False)
#     seat_type = Column(String(20), default="standard")  # standard, vip, etc.
    
#     # Relationships
#     hall = relationship("Hall", back_populates="seats")
#     bookings = relationship("Booking", back_populates="seat")


# class Movie(Base):
#     """Модель фильма"""
#     __tablename__ = "movies"
    
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String(200), nullable=False)
#     description = Column(Text)
#     duration = Column(Integer, nullable=False)  # Продолжительность в минутах
#     poster_url = Column(String(500))
#     country = Column(String(100))
#     director = Column(String(100))
#     created_at = Column(DateTime, default=datetime.utcnow)
    
#     # Relationships
#     sessions = relationship("Session", back_populates="movie")


# class Session(Base):
#     """Модель сеанса"""
#     __tablename__ = "sessions"
    
#     id = Column(Integer, primary_key=True, index=True)
#     movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
#     hall_id = Column(Integer, ForeignKey("halls.id"), nullable=False)
#     start_time = Column(DateTime, nullable=False)
#     price_standard = Column(Float, nullable=False)
#     price_vip = Column(Float, nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
    
#     # Relationships
#     movie = relationship("Movie", back_populates="sessions")
#     hall = relationship("Hall", back_populates="sessions")
#     bookings = relationship("Booking", back_populates="session")


# class Booking(Base):
#     """Модель бронирования"""
#     __tablename__ = "bookings"
    
#     id = Column(Integer, primary_key=True, index=True)
#     session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
#     seat_id = Column(Integer, ForeignKey("seats.id"), nullable=False)
#     user_name = Column(String(100))
#     user_phone = Column(String(20))
#     booking_code = Column(String(50), unique=True, index=True)
#     is_paid = Column(Boolean, default=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
    
#     # Relationships
#     session = relationship("Session", back_populates="bookings")
#     seat = relationship("Seat", back_populates="bookings")


# class User(Base):
#     """Модель администратора"""
#     __tablename__ = "users"
    
#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String(50), unique=True, nullable=False, index=True)
#     email = Column(String(100), unique=True, nullable=False)
#     hashed_password = Column(String(200), nullable=False)
#     is_admin = Column(Boolean, default=False)
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, default=datetime.utcnow)

