from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property

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
    ticket_sell_list:Mapped[list['Ticket_Listing']] = relationship('Ticket_Listing', foreign_keys='Ticket_Listing.seller_id', back_populates="seller")
    ticket_buy_list:Mapped[list['Ticket_Listing']] = relationship('Ticket_Listing', foreign_keys='Ticket_Listing.buyer_id', back_populates="buyer") # back populates off listing rs

class Event(db.Model):
    """Event class contains the details of the event."""
    __tablename__ = 'event'
    event_id:Mapped[int] = mapped_column(Integer, primary_key=True)
    event_name:Mapped[str] = mapped_column(String(120), nullable=False) # Name of event
    event_datetime:Mapped[datetime] = mapped_column(DateTime, nullable=False) # datetime that the event will start at
    location:Mapped[str] = mapped_column(String(120), nullable=False) # Location of event
    description:Mapped[str] = mapped_column(String(120), nullable=True) # Event details
    event_image:Mapped[str] = mapped_column(String(120), nullable=False) # event images directory path/S3 url 

    @hybrid_property
    def status(self)->Mapped[str]:
        """Returns the status of the event depending on the current date."""
        if self.event_datetime >= datetime.now():
            return "Upcoming"
        else:
            return "Ended"

    tickets:Mapped[List['Ticket']] = relationship('Ticket', back_populates="event")
    
    
class Ticket(db.Model):
    """Ticket class contains the details of the ticket.

    INSERT detail data sources: \n
    Blockchain: ticket_id, event_id (take from event name), seat_number, category\n
    Generated: register_date, status, owner_id"""
    __tablename__ = 'ticket'
    ticket_id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False) 
    '''Ticket Blockchain ID, retrieved during Registration phase.'''
    ticket_price_cents:Mapped[int] = mapped_column(Integer, nullable=False) # stored as cents, convert to dollar value for display by /100
    register_date:Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now()) # date when the ticket was registered into system
    '''Datetime object generated when ticket is registered into system'''
    seat_category:Mapped[str] = mapped_column(String(50), nullable=False, default='empty') # pull from BC
    seat_number:Mapped[str] = mapped_column(String(20), nullable=False) # pull from BC
    

    # FK dependencies
    owner_id:Mapped[int] = mapped_column(Integer, ForeignKey('user.user_id'), nullable=False) # added when ticket is registered, updated when bought
    event_id:Mapped[int] = mapped_column(Integer, ForeignKey('event.event_id'), nullable=False) # trace event id from the matching event name

    # ORM Relationship Attribute 
    ticket_listing_history:Mapped[list['Ticket_Listing']] = relationship('Ticket_Listing', back_populates='ticket', lazy=True)
    owner:Mapped["User"] = relationship('User', back_populates="tickets_owned", foreign_keys=[owner_id]) # child of Event
    event:Mapped["Event"] = relationship('Event', back_populates="tickets", foreign_keys=[event_id]) # every ticket has an event linked to it

    @classmethod
    def get_price_str(self, dollarSign:bool=True) -> str: 
        """Returns the listed price as a string in dollar format.\n
        Args:
            dollarSign: Attach a dollar sign to the front, Yes by default
        Format: '$12,345.67' """
        price_str:str = '{:,.2f}'.format(self.ticket_price_cents / 100)

        if dollarSign:
            return '$' + price_str
        else:
            return price_str
    
    @hybrid_property
    def listing_status(self)->Mapped[str]:
        '''Status of ticket\n
        'Not Listed': Default value if the ticket is not listed on the marketplace\n
        'Listed': Value when the ticket is currently available for sale on the marketplace
        '''
        for listing in self.ticket_listing_history:
            if listing.status == 'Available':
                return 'Listed'
        return 'Not Listed'


class Ticket_Listing(db.Model):
    """Tracks the transactions of secondary market ticket sales.\n
    Connected to Ticket (to be sold) and User (Seller,Buyer) tables"""

    __tablename__ = 'ticket_listing'
    listing_id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sale_price_cents:Mapped[int] = mapped_column(Integer, nullable=False, default='0') # divide this value by 100 when displaying so you don't get weird rounding errors
    status:Mapped[str] = mapped_column(String(50), nullable=False, default='Available') 
    '''Status of ticket listing.\n
    Available: Listing is currently available to purchase from and the Ticket's event has not ended yet (No buyer yet)\n
    Sold: Listing is not available to purchase as a buyer has purchased the listed ticket (Has buyer)\n
    Expired: Listing did not sell and the event has ended already (No buyer)'''
    listed_on:Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now()) # tracks when the ticket was put up for sale
    sold_on:Mapped[datetime] = mapped_column(DateTime, nullable=True) # tracks when the listing was sold

    # FK Section
    seller_id:Mapped[int] = mapped_column(Integer, ForeignKey('user.user_id'), nullable=False)
    '''User ID of the seller who listed the ticket'''
    buyer_id:Mapped[int] = mapped_column(Integer, ForeignKey('user.user_id'), nullable=True)
    '''User ID of the buyer who purchased the ticket [Nullable]'''
    ticket_id:Mapped[int] = mapped_column(Integer, ForeignKey('ticket.ticket_id'), nullable=True)

    # ORM Relationship
    seller:Mapped["User"] = relationship(foreign_keys=[seller_id], back_populates="ticket_sell_list") 
    buyer:Mapped[Optional["User"]] = relationship(foreign_keys=[buyer_id], back_populates="ticket_buy_list")
    ticket:Mapped["Ticket"] = relationship('Ticket', back_populates='ticket_listing_history', foreign_keys=[ticket_id]) # every ticket listing has one ticket linked to it whose details you can access through here

    @classmethod
    def get_price_str(self, dollarSign:bool=True) -> str: 
        """Returns the listed price as a string in dollar format.\n
        Args:
            dollarSign: Attach a dollar sign to the front, Yes by default
        Format: '$12,345.67' """
        price_str:str = '{:,.2f}'.format(self.ticket_price_cents / 100)

        if dollarSign:
            return '$' + price_str
        else:
            return price_str
    
    @hybrid_property
    def real_status(self)->Mapped[str]:
        '''Status of ticket listing.\n
        Available: Listing is currently available to purchase from and the Ticket's event has not ended yet (No buyer yet)\n
        Sold: Listing is not available to purchase as a buyer has purchased the listed ticket (Has buyer)\n
        Expired: Listing did not sell and the event has ended already (No buyer)'''
        if self.ticket.event.status == "Ended":
            return "Expired"
        else:
            if self.buyer_id is not None:
                return "Sold"
            else:
                return "Available"

    

    


