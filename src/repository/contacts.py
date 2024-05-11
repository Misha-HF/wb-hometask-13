from sqlalchemy import and_, cast, String
from sqlalchemy.orm import Session
from src.schemas import ContactBase, ContactUpdate, ContactResponse
from src.database.models import Contact
from src.database.models import User
from datetime import date
from sqlalchemy import select
from sqlalchemy import func
from fastapi import HTTPException
from starlette import status
from typing import List, Optional

class ResponseValidationError(Exception):
    pass

async def get_contact(db: Session, user: User, contact_id: int) -> Contact:
    """
    The get_contact function returns a single contact from the database.

    :param db: Access the database
    :param user: Check if the user is authorized to access the contact
    :param contact_id: Specify the id of the contact we want to get
    :return: A ContactResponse object
    """
    res = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    # if not res:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return res


async def get_contact_by_email(db: Session, user: User, email: str) -> List[Contact]:
    """
    The get_contact_by_email function returns a list of contacts that match
    the email address provided
    If no email is provided, all contacts are returned.

    :param db: Connect to the database
    :param user: Get the user id of the logged in user
    :param email: Filter the query by email
    
    
    :return: A list of contacts
    """
    result = db.query(Contact).filter(and_(Contact.email == email, Contact.user_id == user.id)).first()

    return result


async def get_contact_by_phone(db: Session, user: User, phone_number: str) -> List[Contact]:
    """
    The get_contact_by_phone function returns a list of contacts that match
    the phone number provided
    If no phone number is provided, all contacts are returned.

    :param db: Connect to the database
    :param user: Get the user id of the logged in user
    :param phone_number: Filter the query by phone number
    
    
    :return: A list of contacts
    """
    result = db.query(Contact).filter(and_(Contact.phone_number == phone_number, Contact.user_id == user.id)).first()

    return result


async def get_contacts(db: Session, user: User, skip: int = 0, limit: int = 100) -> List[Contact]:
    """
    The get_contacts function returns a list of contacts for the user.
    The function takes in three parameters: skip, limit, and user.
    Skip is an integer that determines how many contacts to skip over
    before returning results.
    Limit is an integer that determines how many results to return after
    skipping over the specified number of contacts.
    User is a User object containing information about the current
    logged-in user.

    :param db: Pass the database session to the function
    :param user: Get the user_id from the user object
    :param skip: Skip the first n contacts
    :param limit: Limit the number of contacts returned
    
    :return: A list of contacts
    """
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


async def create_contact(db: Session, user: User, contact: ContactBase) -> Contact:
    """
    The create_contact function creates a new contact in the database.

    :param db: Pass the database session to the function
    :param user: Get the user id from the token
    :param contact: Created contact object
    
    :return: A contact response object, that was created
    """
    db_contact = Contact(**contact.dict(), user_id=user.id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


async def update_contact(db: Session, user: User, db_contact: Contact, contact: ContactUpdate) -> Contact:
    """
    The update_contact function updates a contact in the database.

    :param db: Access the database
    :param user: Get the user id of the current logged in user
    :param db_contact: The contact that will be changed
    :param contact: The contact will be changed
    
    
    :return: A contact response object, that was updated
    """
    if db_contact.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You don't have permission to update this contact")
    if contact.first_name:
        db_contact.first_name = contact.first_name
    if contact.last_name:
        db_contact.last_name = contact.last_name
    if contact.email:
        db_contact.email = contact.email
    if contact.phone_number:
        db_contact.phone_number = contact.phone_number
    if contact.birthday:
        db_contact.birthday = contact.birthday
    db.commit()
    db.refresh(db_contact)
    return db_contact


async def delete_contact(db: Session, user: User, contact_id: int) -> None:
    """
    The delete_contact function deletes a contact from the database.

    :param db: Connect to the database
    :param user: Get the user id from the database
    :param contact_id: Identify the contact to be deleted
    
    :return: Contact that was deleted
    """
    contact = await get_contact(db, user, contact_id)
    if contact is None:
        raise HTTPException
    
    db.delete(contact)
    db.commit()


async def search_contacts(db: Session, user: User, first_name: str = None, last_name: str = None, email: str = None)-> List[Contact]:
    """
    The search_contacts function returns a list of contacts with the
    given first_name, last_name or email.

    :param db: Pass the database session to the function
    :param user: Get the user id from the database
    :param first_name: First name of contact
    :param last_name: Last name of contact
    :param email: Email of contact
    :return: A list of ContactResponse objects
    """
    conditions = [Contact.user_id == user.id]  # Додали умову для user_id
    if first_name:
        conditions.append(Contact.first_name == first_name)
    if last_name:
        conditions.append(Contact.last_name == last_name)
    if email:
        conditions.append(Contact.email == email)
    if not conditions:
        raise ResponseValidationError("Please provide at least one search condition.")
    query = db.query(Contact).filter(and_(*conditions)).all()
    return query


# for postgres

async def get_contacts_by_birthday(db: Session, user: User, start_date: date, end_date: date) -> Optional[List[Contact]]:
    """
    The get_birthdays function returns a list of contacts with birthdays in
    the next 7 days.

    :param db: Pass the database session into the function
    :param user: Get the user id
    :param start_date: current date
    :param end_date: date after 7 days
    :return: A list of contacts that have a birthday within the next 7 days
    """
        # result = db.query(Contact).filter(and_(Contact.email == email, Contact.user_id == user.id)).all()
    result = db.query(Contact).where(
        and_(
            cast(func.strftime('%m%d', Contact.birthday), String) >= start_date.strftime('%m%d'),
            cast(func.strftime('%m%d', Contact.birthday), String) <= end_date.strftime('%m%d'),
            (Contact.user_id == user.id)
        )
    ).all()
    
    
    return result


#for sqlite
# async def get_contacts_by_birthday(db: Session, user: User, start_date: date, end_date: date):
    """
    The get_birthdays function returns a list of contacts with birthdays in
    the next 7 days.

    :param db: Pass the database session into the function
    :param user: Get the user id
    :param start_date: current date
    :param end_date: date after 7 days
    :return: A list of contacts that have a birthday within the next 7 days
    """
#     query = select(Contact).where(
#         and_(
#             cast(func.strftime('%m%d', Contact.birthday), String) >= start_date.strftime('%m%d'),
#             cast(func.strftime('%m%d', Contact.birthday), String) <= end_date.strftime('%m%d'),
#             (Contact.user_id == user.id)
#         )
#     )
#     result = db.execute(query)
#     return result.scalars().all()


