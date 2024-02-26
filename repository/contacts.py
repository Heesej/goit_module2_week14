from datetime import datetime, timedelta
from typing import List
from sqlalchemy import extract, and_, or_
from sqlalchemy.orm import Session
from database.models import Contact, User
from schemas import ContactBase


async def get_contacts(
        first_name: str | None,
        last_name: str | None,
        email: str | None,
        skip: int,
        limit: int,
        user: User,
        db: Session
) -> List[Contact]:
    """
    The get_contacts function returns a list of contacts that match the given parameters.

    :param first_name: str: Filter the contacts by first name
    :param last_name: str: Filter the contacts by last name
    :param email: str: Filter the contacts by email
    :param skip: int: Skip a number of records
    :param limit: int: Limit the number of results returned
    :param user: User: Get the user id from the current logged in user
    :param db: Session: Pass the database session to the function.
    :return: A list of matching contacts
    """
    query = db.query(Contact).filter(Contact.user_id == user.id)

    filter_conditions = []
    if first_name is not None:
        filter_conditions.append(Contact.first_name == first_name)
    if last_name is not None:
        filter_conditions.append(Contact.last_name == last_name)
    if email is not None:
        filter_conditions.append(Contact.email == email)

    if filter_conditions:
        query = query.filter(*filter_conditions)

    return query.offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:

    """
    The get_contact function takes in a contact_id and returns the contact with that id from database.

    :param contact_id: int: Identify the contact to be retrieved
    :param user: User: Get the user id from the current logged in user
    :param db: Session: Pass the database session to the function
    :return: The contact with the given id
    """
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: ContactBase, user: User, db: Session) -> Contact:

    """
    The create_contact function creates a new contact in the database.

    :param body: ContactBase: Pass the contact data from the request body to create_contact
    :param user: User: Get the user id from the current logged in user
    :param db: Session: Access the database
    :return: A contact object
    """
    contact = Contact(first_name=body.first_name,
                      last_name=body.last_name,
                      email=body.email,
                      phone=body.phone,
                      date_of_birth=body.date_of_birth,
                      additional_data=body.additional_data,
                      user_id=user.id
                      )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def check_contact(email: str, phone: str, user: User, db: Session) -> Contact:

    """
    The check_contact function checks if a contact already exists in the database.

    :param email: str: Check if the email is already in use by another user
    :param phone: str: Check if the phone number is already in the database
    :param user: User: Get the user id from the current logged in user
    :param db: Session: Pass the database session to the function
    :return: A contact object if the email or phone number is already in database
    """
    return db.query(Contact).filter(
        and_(Contact.user_id == user.id, or_(Contact.email == email, Contact.phone == phone))).first()


async def update_contact(contact_id: int, body: ContactBase, user: User, db: Session) -> Contact | None:

    """
    The update_contact function takes in a contact_id and updates the contact in the database.

    :param contact_id: int: Identify which contact to update
    :param body: ContactBase: Pass the data from the request body to this function
    :param user: User: Get the user id from the current logged in user
    :param db: Session: Access the database
    :return: The updated contact or none if no contact was found
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.date_of_birth = body.date_of_birth
        contact.additional_data = body.additional_data
        db.commit()
    return contact


async def remove_contact(contact_id: int, user: User, db: Session) -> Contact | None:

    """
    The remove_contact function removes a contact from the database.

    :param contact_id: int: Specify the id of the contact to be removed
    :param user: User: Get the user id from the current logged in user
    :param db: Session: Pass the database session to the function
    :return: The contact that was removed
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def birthdays_in_7_days(skip: int, limit: int, user: User, db: Session) -> List[Contact]:

    """
    The birthdays_in_7_days function returns a list of contacts whose birthdays are within the next 7 days.
        User is the current logged in user who's contacts will be returned.

    :param skip: int: Skip a number of records from the database
    :param limit: int: Limit the number of results returned
    :param user: User is the current logged in user who's contacts will be returned.
    :param db: Session: Pass the database session to the function
    :return: A list of contacts whose birthday is within the next 7 days
    """
    today_date = datetime.now().date()
    end_date = today_date + timedelta(days=7)

    if today_date.month == end_date.month:
        results = db.query(Contact).filter(
            and_(Contact.user_id == user.id, (
                    (extract("month", Contact.date_of_birth) == today_date.month) &
                    (extract("day", Contact.date_of_birth) >= today_date.day) &
                    (extract("day", Contact.date_of_birth) <= end_date.day))
                 )
        ).offset(skip).limit(limit).all()
    else:
        results = db.query(Contact).filter(
            and_(Contact.user_id == user.id, (
                    (extract("month", Contact.date_of_birth) == end_date.month) &
                    (extract("day", Contact.date_of_birth) <= end_date.day)
                    | (
                            (extract("month", Contact.date_of_birth) == today_date.month) &
                            (extract("day", Contact.date_of_birth) >= today_date.day))
            )
                 )
        ).offset(skip).limit(limit).all()
    return results
