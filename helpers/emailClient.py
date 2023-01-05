import smtplib
from pathlib import Path
import ssl
from threading import Thread
import json
import os
import socket

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from datetime import datetime

class EmailClient(Thread):

    def __init__(self, password, sender, receiver) -> None:
        #super(EmailClient, self).__init__()
        Thread.__init__(self)

        self.ctx = ssl.create_default_context()
        self.password = password
        self.sender = sender
        self.receiver = receiver
        print("email thread started")
    
    def message_template(self, user, file_size, content):
        """
        constructs a html and plain messages either of which will sent to the receiver
        depending on the receiver's email client compatibility
        ---------------
        return:
            :html: HTML message format
            :plain: string message format
        """
    
        html = f"""\
                    <html>
                    <body>
                        <p>
                            Server: {user}
                        </p>
                         <p>
                            Date: {datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}
                        </p>
                        <h2>
                            File Size:
                            <b><u><i>{file_size}</i></u></b>
                        </h2>
                        <h4> Content </h4>
                        <p>
                            {content}
                        </p>
                    </body>
                    <footer>
                        <p><i>{datetime.now().year}</i></P>
                    </footer>
                    </html>
                """

        plain = f"""\
                \t Server: {user} \n
                \t Date: {datetime.now()} \n \n
                \t File Size: {file_size} \n
                Content: \n
                {content}
                """

        return html, plain

    def send_email(self, user:str, file_size:int, content:str, attachment=None) -> None:
        """
        Sends the user's ip, copied file size, content, and attachment to the email address specified
        ---------------------
        return:
            :user: ip address of the user's machine
            :file_size: size of the file copied
            :content: the actual content of the file (str). only applicable to text
            :attachment: the file (byte) or image copied 
        """
        print("file sending..", user, file_size, content, attachment)

        message = MIMEMultipart("alternative")
        message["Subject"] = f"Suspicious Activity Detected - Server: {user}"
        message["From"] = self.sender
        message["To"] = self.receiver

        html, plain = self.message_template(user, file_size, content)

        message.attach(MIMEText(plain, "plain"))
        message.attach(MIMEText(html, "html"))

        #: If there is an attachment (Image or File)
        if attachment:
            file = MIMEApplication(attachment)
            description = f"Size: {file_size}, Agent: {user}"
            file.add_header("File:", description)
            message.attach(file)

        with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=self.ctx) as server:
            server.login(self.sender, self.password)
            server.sendmail(self.sender, self.receiver, message.as_string())


