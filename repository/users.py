from libgravatar import Gravatar
from sqlalchemy.orm import Session

from database.models import User
from schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:

    """
    The get_user_by_email function returns the user with that email. If no such user exists, it returns None.

    :param email: str: Pass in the email address of the user you want to get from the database
    :param db: Session: Pass the database session to the function
    :return: The user with the given email
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:

    """
    The create_user function creates a new user in the database with parameters include in UserModel.

    :param body: UserModel: Pass the user data to the database
    :param db: Session: Pass the database session to the function
    :return: A user object
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:

    """
    The update_token function updates the refresh token for a user in the database.

    :param user: User: Identify the user that is being updated
    :param token: str | None: Set the refresh token for a user
    :param db: Session: Pass the database session to the function
    """
    user.refresh_token = token
    db.commit()


async def confirm_email(email: str, db: Session) -> None:

    """
    The confirm_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.

    :param email: str: Get the user's email address
    :param db: Session: Pass the database session to the function
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:

    """
    The update_avatar function updates the avatar of a user in the database.

    :param email: Pass the email of the user for whom the avatar will be changed
    :param url: str: Pass in the url of the avatar image
    :param db: Session: Pass the database session to the function
    :return: The updated user object
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
