from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors

from conf.config import settings
from services.auth import auth_service

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="Example mail",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email: str, username: str, host: str):

    """
    The send_email function sends an email to the user with a link that they can click on to verify their account.
        The function takes in three parameters:
            - email: the user's email address, which is used as a unique identifier for each user.
            - username: the username of the new account being created. This is used in personalizing emails sent out by
                        FastMail and also displayed on our website when users log into their accounts.
            - host: this parameter specifies what domain name we are using for our website (e.g., localhost). It is needed
                    because we need

    :param email: str: Specify the email address of the user
    :param username: str: Pass the username to the email template
    :param host: str: Send the host name to the email template
    :return: A coroutine object
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)
