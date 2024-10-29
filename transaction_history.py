from models import User, Ticket_Listing
from operator import attrgetter
"""Functions for the User Transaction History page"""


# for sell listings, must check if the listing status is "Sold", do not include if it is still "Available"
def buyListTransTable(buyList: list[Ticket_Listing])->list:
    """Generates a list of converted buy listing records sorted from newest to oldest purchase date.
    
    Sorts through the ticket_buy_list attribute of the user object and converts the ticket_listing objects
    into dictionary objects.
    Dict objects are then placed into "page" lists based on the recordPerPage count and 
    finally combined into a big list.

    Args: 
        user: User Model object containing the buy listing attribute
        recordPerPage: Number of records that should be displayed on a page

    Returns:
        The buy list for the Transaction History HTML table.

    Raises:
        AttributeError: If specified user does not have a buy list
    """
    
    buyList.sort(key=attrgetter('sold_on'), reverse=True) # sorts the buyList from Newest to Oldest 
    converted_list = []

    for listing in buyList: # as buy listings are done from the pov of the buyer, they will always have a seller ID
        converted_list.append(listingToDict(listing)) # adds the converted dict obj
    
    return converted_list

def saleListTransTable(sale_list: list[Ticket_Listing])->list[dict[str,str]]:
    """Generates a list of converted sale listing records sorted from newest to oldest sell date listing."""

    sale_list.sort(key=attrgetter('sold_on'), reverse=True)
    converted_list = []

    for listing in sale_list:
        if listing.status == "Sold": # skip listings that are Available as they do not have a buyer ID
            converted_list.append(listingToDict(listing,buyOrSell=False))
    
    return converted_list

def listingToDict(listing:Ticket_Listing, buyOrSell:bool=True)->dict[str, str]:
    """Converts a listing object into a buy or sell listing dict usable by the Transaction History Table.
    
    Args:
        listing: the ticket_listing object to convert into a buy listing dict.
        buyOrSell: True: buy history listing, False: sell history listing
        
    Returns:
        A dict of buy listing information (str) with 4 key values: date, event_name, seller_name/buyer_name, price. 

        For example:
        {'date': "25 Dec 2024",
         'event_name': "Fright Night",
         'seller_name': "Jim Morrison",
         'price': "$24,120.98"}
         
    """
    
    try:
        listing_dict = {} # declares the dict object
        listing_dict['date'] = listing.sold_on.strftime("%d %b %Y") # converts the sold_on datetime object into a string in the format 'DD MMM YYYY'
        listing_dict['event_name'] = listing.ticket.event.event_name # gets the event name from the Event object
        if buyOrSell: # changes the dict field depending the argument
            listing_dict['seller_name'] = f"{listing.seller.first_name} {listing.seller.last_name}"  # gets the sellers first and last name and combines them 
        else:
            listing_dict['buyer_name'] = f"{listing.buyer.first_name} {listing.buyer.last_name}"
        listing_dict['price'] = listing.get_price_str() 
    except AttributeError:
        raise AttributeError()

    return listing_dict

def sliceListIntoPages(fullList:list, pageSize:int=10, pageNum:int=1)->list[dict]:
    '''Returns a section (page) of the list based on page size and page number

    Args:
        fullList: List to be split up
        pageSize: Number of records to display on the page
        pageNum: selected page of records to display
    
    Returns:
        slice of the page based on the args'''
        
    start_index = (pageNum - 1) * pageSize  # first record in page to display
    end_index = start_index + pageSize # last record in page to display
    selected_page_list = fullList[start_index:end_index] # gets a slice of the list based on start and end indexes

    return selected_page_list   
