from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Time, ForeignKey
from typing import List, Optional
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
    
    tickets_owned:Mapped[list['Ticket']] = relationship('Ticket', back_populates="owner", lazy=True)
    ticket_sell_list:Mapped[list['Ticket_Listing']] = relationship('Ticket_Listing', back_populates="seller")
    ticket_buy_list:Mapped[list['Ticket_Listing']] = relationship('Ticket_Listing', back_populates="buyer") # back populates off listing rs

class Event(db.Model):
    """Event class contains the details of the event."""
    __tablename__ = 'event'
    event_id:Mapped[int] = mapped_column(Integer, primary_key=True)
    event_name:Mapped[str] = mapped_column(String(120), nullable=False) # Name of event
    event_datetime:Mapped[datetime] = mapped_column(DateTime, nullable=False) # datetime that the event will start at
    #time:Mapped[time] = mapped_column(Time, nullable=False) #TODO come back here ltr
    location:Mapped[str] = mapped_column(String(120), nullable=False) # Location of event
    description:Mapped[str] = mapped_column(String(120), nullable=True) # Event details
    event_image:Mapped[str] = mapped_column(String(120), nullable=False) # event images directory path/S3 url 
    
    tickets:Mapped[List['Ticket']] = relationship('Ticket', back_populates="event")
    
    
class Ticket(db.Model):
    """Ticket class contains the details of the ticket."""
    __tablename__ = 'ticket'
    ticket_id:Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_price_cents:Mapped[int] = mapped_column(Integer, nullable=False)
    purchase_date:Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())
    seat_category:Mapped[str] = mapped_column(String(50), nullable=False, default='empty')
    
    owner_id:Mapped[int] = mapped_column(Integer, ForeignKey('user.user_id'), nullable=False) # FK dependency
    event_id:Mapped[int] = mapped_column(Integer, ForeignKey('event.event_id'), nullable=False)

    ticket_listing_history:Mapped[list['Ticket_Listing']] = relationship('Ticket_Listing', back_populates='ticket', lazy=True)
    owner:Mapped["User"] = relationship('User', back_populates="tickets_owned", foreign_keys=[owner_id]) # child of Event
    event:Mapped["Event"] = relationship('Event', back_populates="tickets", foreign_keys=[event_id]) # every ticket has an event linked to it

    def get_price_str(self) -> str: 
        """Returns the listed price as a string in dollar format."""
        return '${:,.2f}'.format(self.ticket_price_cents / 100)


class Ticket_Listing(db.Model):
    """Tracks the transactions of secondary market ticket sales."""
    __tablename__ = 'ticket_listing'
    listing_id:Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_price_cents:Mapped[int] = mapped_column(Integer, nullable=False, default='0') # divide this value by 100 when displaying so you don't get weird rounding errors
    status:Mapped[str] = mapped_column(String(50), nullable=False, default='Available') # status of ticket listing: Available/Sold/Reserved?/Removed
    listed_on:Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now()) # tracks when the ticket was put up for sale
    sold_on:Mapped[datetime] = mapped_column(DateTime, nullable=True) # tracks when the listing was sold

    seller_id:Mapped[int] = mapped_column(Integer, ForeignKey('user.user_id'), nullable=False)
    buyer_id:Mapped[int] = mapped_column(Integer, ForeignKey('user.user_id'), nullable=True)
    ticket_id:Mapped[int] = mapped_column(Integer, ForeignKey('ticket.ticket_id'), nullable=True)

    seller:Mapped["User"] = relationship(foreign_keys=[seller_id], back_populates="ticket_sell_list") 
    buyer:Mapped[Optional["User"]] = relationship(foreign_keys=[buyer_id], back_populates="ticket_buy_list")
    ticket:Mapped["Ticket"] = relationship('Ticket', back_populates='ticket_listing_history', foreign_keys=[ticket_id]) # every ticket listing has one ticket linked to it whose details you can access through here

    def get_price_str(self) -> str: 
        """Returns the listed price as a string in dollar format."""
        return '${:,.2f}'.format(self.sale_price_cents / 100)
    


