from sqlalchemy import and_, cast, String
from sqlalchemy.orm import Session
from src import schemas
from src.database.models import Contact
from src.database.models import User
from datetime import date
from sqlalchemy import select
from sqlalchemy import func
from fastapi import HTTPException
from starlette import status

class ResponseValidationError(Exception):
    pass

async def get_contact(db: Session, user: User, contact_id: int):
    result = db.execute(select(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id))
    contact = result.scalars().first()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


async def get_contact_by_email(db: Session, user: User, email: str):
    result = db.execute(select(Contact).filter(Contact.email == email, Contact.user_id == user.id))
    contact = result.scalars().first()

    return contact


async def get_contact_by_phone(db: Session, user: User, phone_number: str):
    result = db.execute(select(Contact).filter(Contact.phone_number == phone_number, Contact.user_id == user.id))
    contact = result.scalars().first()

    return contact


async def get_contacts(db: Session, user: User, skip: int = 0, limit: int = 100):
    result = db.execute(select(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit))
    contacts = result.scalars().all()
    return contacts


async def create_contact(db: Session, user: User, contact: schemas.ContactCreate):
    db_contact = Contact(**contact.dict(), user_id=user.id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


async def update_contact(db: Session, user: User, db_contact: Contact, contact: schemas.ContactUpdate):
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


async def delete_contact(db: Session, user: User, contact_id: int):
    db_contact = await get_contact(db, user, contact_id)
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact


async def search_contacts(db: Session, user: User, first_name: str = None, last_name: str = None, email: str = None):
    conditions = [Contact.user_id == user.id]  # Додали умову для user_id
    if first_name:
        conditions.append(Contact.first_name == first_name)
    if last_name:
        conditions.append(Contact.last_name == last_name)
    if email:
        conditions.append(Contact.email == email)
    if not conditions:
        raise ResponseValidationError("Please provide at least one search condition.")
    query = select(Contact).filter(and_(*conditions))
    result = db.execute(query)
    return result.scalars().all()


# для постгрес

async def get_contacts_by_birthday(db: Session, user: User, start_date: date, end_date: date):
    query = select(Contact).where(
        func.date_part('month', Contact.birthday).between(start_date.month, end_date.month) &
        func.date_part('day', Contact.birthday).between(start_date.day, end_date.day) &
        (Contact.user_id == user.id)  # Додано умову для user_id
    )
    result = db.execute(query)
    return result.scalars().all()


#for sqlite
# async def get_contacts_by_birthday(db: Session, user: User, start_date: date, end_date: date):
#     query = select(Contact).where(
#         and_(
#             cast(func.strftime('%m%d', Contact.birthday), String) >= start_date.strftime('%m%d'),
#             cast(func.strftime('%m%d', Contact.birthday), String) <= end_date.strftime('%m%d'),
#             (Contact.user_id == user.id)
#         )
#     )
#     result = db.execute(query)
#     return result.scalars().all()


