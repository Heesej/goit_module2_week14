from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter

from sqlalchemy.orm import Session

from database.db import get_db
from database.models import User
from schemas import ContactBase, ContactResponse
from repository import contacts as repository_contacts
from services.auth import auth_service

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/birthday", response_model=List[ContactResponse])
async def read_contacts_with_birthday(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):

    """
    The read_contacts_with_birthday function returns a list of contacts with birthdays in the next 7 days.

    :param skip: int: Skip a number of records in the database
    :param limit: int: Limit the number of contacts returned
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user from the auth_service
    :return: A list of contacts
    """
    contacts = await repository_contacts.birthdays_in_7_days(skip, limit, current_user, db)
    return contacts


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):

    """
    The read_contacts function returns the list of user's all contacts.

    :param first_name: str: Specify the first name of the contact to be retrieved
    :param last_name: str: Filter the contacts by last name
    :param email: str: Filter the contacts by email
    :param skip: int: Skip the first n contacts
    :param limit: int: Limit the number of contacts returned
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the user object of the currently logged-in user
    :return: A list of contacts
    """
    contacts = await repository_contacts.get_contacts(first_name, last_name, email, skip, limit, current_user, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
        contact_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):

    """
    The read_contact function will return a contact by its id.

    :param contact_id: int: Specify the contact id to be used in the function
    :param db: Session: Get a database session
    :param current_user: User: Get the user object of the currently logged-in user
    :return: A contact object
    """
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactBase, dependencies=[Depends(RateLimiter(times=1, seconds=10))], status_code=status.HTTP_201_CREATED)
async def create_contact(
        body: ContactBase,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):

    """
    The create_contact function creates a new contact in the database.

    :param body: ContactBase: Get the data from the request body
    :param db: Session: Get the database session
    :param current_user: User: Get the user object of the currently logged-in user
    :return: A contactbase object
    """
    exist_contact = await repository_contacts.check_contact(body.email, body.phone, current_user, db)
    if exist_contact:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or phone number exists.")
    return await repository_contacts.create_contact(body, current_user, db)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
        body: ContactBase,
        contact_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):

    """
    The update_contact function takes in a contact_id and updates the contact in the database.

    :param body: ContactBase: Get the data from the request body
    :param contact_id: int: Specify the contact that will be deleted
    :param db: Session: Get a database session
    :param current_user: User: Get the user object of the currently logged-in user
    :return: A contact object
    """
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
        contact_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):

    """
    The remove_contact function takes in a contact_id and removes the contact from the database.

    :param contact_id: int: Identify the contact to be removed
    :param db: Session: Get the database session
    :param current_user: User: Get the user object of the currently logged-in user
    :return: The contact that was removed
    """
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
