import ssl
import smtplib
import configparser
import logging
from datetime import datetime
from typing import Tuple
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

config = configparser.ConfigParser()
config.read("amserver.ini")

logger = logging.getLogger("Email")
logger.setLevel(logging.INFO)
# Create file handler to keep logs.
file_logger = logging.FileHandler("email.log")
file_formater = logging.Formatter(
    "%(asctime)s - %(name)s %(levelname)s - %(message)s", 
)
file_logger.setFormatter(file_formater)
logger.addHandler(file_logger)

def alert(content: str):
    """
    Get email configuration and pass to function that will send the
    email notification.
    """
    # Get sender, password, and receiver details from config file.
    try:
        sender = config["EMAIL"]["email_host_user"]
        password = config["EMAIL"]["email_host_password"]
        receiver = config["EMAIL"]["admin_email"]

        send_email(sender, password, receiver, content)
        logger.info(f"Email sent to {receiver}")
    except Exception as ex:
        logger.exception(str(ex))

def send_email(sender: str, password: str, receiver: str, content: str):
    """
    Sends an email containing `content` to the receiver.

    Parameters
    ----------
    sender: str
        Email address from which you want to send emails (host email).
    password: str
        Password associated with your host email account.
    receiver: str
        Receiver's email address where you want to send the alert.
    content: str
        Content of the message body.
    """
    ctx = ssl.create_default_context()
    message = MIMEMultipart("alternative")
    message["Subject"] = "User Session Terminated"
    message["From"] = sender
    message["To"] = receiver

    html, plain = template(content)

    message.attach(MIMEText(plain, "plain"))
    message.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=ctx) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, message.as_string())

def template(content: str) -> Tuple[str, str]:
        """
        Constructs an html and plain message, either of which will be
        sent to the receiver depending on the receiver's email client
        compatibility.

        Returns
        -------
        Tuple[str, str]
            HTML message format and string/plain message format.
        """
        html = f"""\
                    <html>
                    <body>
                        <p>
                            {content}
                        </p>
                        <p>
                            Date: {datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}
                        </p>
                    </body>
                    <footer>
                        <p><i>Log Cycler ({datetime.now().year})</i></p>
                    </footer>
                    </html>
                """

        plain = f"""\
                \t {content} \n
                \t Date: {datetime.now()} \n \n
                """

        return html, plain