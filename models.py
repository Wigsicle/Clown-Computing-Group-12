from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Time, ForeignKey
from db import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'user'
    user_id: Mapped[int] = mapped_column(primary_key=True)
    email:Mapped[str] = mapped_column(String(255), unique=True,nullable=False)
    password:Mapped[str] = mapped_column(String(255), nullable=False)
    user_type:Mapped[str] = mapped_column(String(45), nullable=False)
    first_name:Mapped[str] = mapped_column(String(50), nullable=False)
    last_name:Mapped[str] = mapped_column(String(50), nullable=False)
    
    tickets:Mapped[list['Ticket']] = relationship('Ticket', backref='user', lazy=True)
    ticket_transactions:Mapped[list['Ticket_Listing']] = relationship('Ticket_Listing', backref='ticket_listing', lazy=True)
    
class Event(db.Model):
    __tablename__ = 'event'
    event_id:Mapped[int] = mapped_column(Integer, primary_key=True)
    event_name:Mapped[str] = mapped_column(String(120), nullable=False)
    event_datetime:Mapped[datetime] = mapped_column(DateTime, nullable=False)
    #time:Mapped[time] = mapped_column(Time, nullable=False) #TODO come back here ltr
    location:Mapped[str] = mapped_column(String(120), nullable=False)
    description:Mapped[str] = mapped_column(String(120), nullable=False)
    event_image:Mapped[str] = mapped_column(String(120), nullable=False)
    
    tickets:Mapped[list['Ticket']] = relationship('Ticket', backref='event', lazy=True)
    
    
class Ticket(db.Model):
    __tablename__ = 'ticket'
    ticket_id:Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_price_cents:Mapped[int] = mapped_column(Integer, nullable=False)
    purchase_date:Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())
    seat_category:Mapped[str] = mapped_column(String(50), nullable=False, default='empty')
    
    owner_id:Mapped[int] = mapped_column(Integer, ForeignKey('user.user_id'), nullable=False) # FK dependency
    event_id:Mapped[int] = mapped_column(Integer, ForeignKey('event.event_id'), nullable=False)

    ticket_listing_history:Mapped[list['Ticket_Listing']] = relationship('Ticket_Listing', backref='ticket_listing', lazy=True)

    def get_price_str(self) -> str: 
        return '${:,.2f}'.format(self.ticket_price_cents / 100)


class Ticket_Listing(db.Model):
    __tablename__ = 'ticket_listing'
    listing_id:Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_price_cents:Mapped[int] = mapped_column(Integer, nullable=False, default='0') # divide this value by 100 when displaying so you don't get weird rounding errors
    status:Mapped[str] = mapped_column(String(50), nullable=False, default='Available')

    seller_id:Mapped[int] = mapped_column(Integer, ForeignKey('user.user_id'), nullable=False)
    buyer_id:Mapped[int] = mapped_column(Integer, ForeignKey('user.user_id'), nullable=True)
    ticket_id:Mapped[int] = mapped_column(Integer, ForeignKey('ticket.ticket_id'), nullable=True)

    def get_price_str(self) -> str: 
        return '${:,.2f}'.format(self.sale_price_cents / 100)

