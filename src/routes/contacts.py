from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta
from src import schemas
from src.repository import contacts
from src.database.db import get_db
from src.services.auth import auth_service
from src.database.models import User
from src.repository import contacts
from fastapi_limiter.depends import RateLimiter

router = APIRouter()


@router.post("/contacts/", response_model=schemas.ContactResponse, status_code=status.HTTP_201_CREATED, description='No more than 10 requests per minute', dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact in the database.

    :param contact: Get the data from the request body
    :param db: Pass the database session to the repository layer
    :param current_user: Get the user that is currently logged in
    :return: Created contact object
    """
    db_contact_by_email = await contacts.get_contact_by_email(db, user=current_user, email=contact.email)
    db_contact_by_phone = await contacts.get_contact_by_phone(db, user=current_user, phone_number=contact.phone_number)
    if db_contact_by_email or db_contact_by_phone:
        raise HTTPException(status_code=400, detail="Email or phone number already registered")
    return await contacts.create_contact(db=db, user=current_user, contact=contact)


@router.get("/contacts/", response_model=List[schemas.ContactResponse])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_contacts function returns a list of contacts for the current user.

    :param skip: Skip a certain amount of contacts
    :param limit: Limit the number of contacts returned
    :param db: Pass the database session to the repository layer
    :param current_user: Get the current user from the auth_service
    :return: A list of contactresponse objects
    """
    contacts_list = await contacts.get_contacts(db, user=current_user, skip=skip, limit=limit)
    return contacts_list


@router.get("/contacts/{contact_id}", response_model=schemas.ContactResponse)
async def read_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_contact function returns a single contact from the database.

    :param contact_id: Identify the contact to be retrieved
    :param db: Get the database session
    :param current_user: Get the current user from the database
    :return: A contactresponse object
    """
    db_contact = await contacts.get_contact(db, user=current_user, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.get("/contacts/search/", response_model=List[schemas.ContactResponse])
async def search_contacts(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    The search_contact function allows the user to search for contacts by
    first_name, last_name or email.

    :param first_name: Specify that the first_name parameter is optional
    :param last_name: Get the last_name from the query string
    :param email: Search for a contact by email
    :param db: Pass the database session to the function
    :param current_user: Get the current user
    :return: A list of contactresponse objects, depending on the query parameters
    """
    contacts_list = await contacts.search_contacts(db, user=current_user, first_name=first_name, last_name=last_name, email=email)
    return contacts_list


@router.get("/contacts/birthdays/", response_model=List[schemas.ContactResponse])
async def get_upcoming_birthdays(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_upcoming_birthdays function returns a list of contacts that have birthdays
    in the current week.

    :param db: Pass the database connection to the repository layer
    :param current_user: Get the current user
    :return: A list of contactresponse objects
    """
    today = date.today()
    week_later = today + timedelta(days=7)
    contacts_list = await contacts.get_contacts_by_birthday(db, user=current_user, start_date=today, end_date=week_later)
    return contacts_list



@router.put("/contacts/{contact_id}", response_model=schemas.ContactResponse)
async def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.

    :param contact_id: Identify the contact to be updated
    :param contact: Get the contact information from the request body
    :param db: Access the database
    :param current_user: Get the current user
    :return: An updated contact object
    """
    db_contact = await contacts.get_contact(db, user=current_user, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    if contact.email and contact.email != db_contact.email:
        db_duplicate_email = await contacts.get_contact_by_email(db, user=current_user, email=contact.email)
        if db_duplicate_email:
            raise HTTPException(status_code=400, detail="Email already registered")
    if contact.phone_number and contact.phone_number != db_contact.phone_number:
        db_duplicate_phone = await contacts.get_contact_by_phone(db, user=current_user, phone_number=contact.phone_number)
        if db_duplicate_phone:
            raise HTTPException(status_code=400, detail="Phone number already registered")
    return await contacts.update_contact(db=db, user=current_user, db_contact=db_contact, contact=contact)



@router.delete("/contacts/{contact_id}", response_model=schemas.ContactResponse)
async def delete_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The delete_contact function deletes a contact from the database.

    :param contact_id: Specify the id of the contact that is to be deleted
    :param db: Pass the database session to the repository layer
    :param current_user: Get the current user from the token
    :return: None
    """
    db_contact = await contacts.get_contact(db, user=current_user, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return await contacts.delete_contact(db=db, user=current_user,contact_id=contact_id) 