"""This will handle achiving and auto deleting old logs."""
import os
import shutil
import smtplib
import ssl
import threading
import sched
import time
import subprocess
import logging
import socket
from pathlib import Path
from typing import Tuple
from datetime import datetime
from configparser import ConfigParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import ffmpeg

config = ConfigParser()
config.read("amserver.ini")

logger = logging.getLogger("Cycler")
logger.setLevel(logging.INFO)
# Create file handler to keep logs.
file_logger = logging.FileHandler("cycle.log")
file_formater = logging.Formatter(
    "%(asctime)s - %(name)s %(levelname)s - %(message)s", 
)
file_logger.setFormatter(file_formater)
logger.addHandler(file_logger)

class LogCycler(threading.Thread):
    interval = float(config["CYCLER"]["interval"])
    fraction = float(config["CYCLER"]["fraction_left"])
    days_old = int(config["CYCLER"]["days_old"])
    vid_dir = config["CYCLER"]["directory"]
    arc_dir = config["CYCLER"]["archive_dir"]
    quality = config["CYCLER"]["quality"]

    def __init__(self, **kwargs):
        super(LogCycler, self).__init__(**kwargs)
    
    def run(self):
        my_scheduler = sched.scheduler(time.monotonic, time.sleep)
        my_scheduler.enter(1, 1, self.action, (my_scheduler,))
        my_scheduler.run()
        pass

    # Run once every hour I think
    def action(self, scheduler: sched.scheduler):
        # Schedule next call.
        scheduler.enter(self.interval, 1, self.action, (scheduler,))
        # Get the usage statistics of the drive.
        stats = shutil.disk_usage(os.path.sep)
        percentage_left = (stats[2]/stats[0]) * 100
        # Check if free space is less than 5% of total storage.
        if percentage_left < 5:
            self.delete_video_logs()
        # Check video files and check if any are older than 3 days.
        now = time.time()
        video_log_dir = Path(self.vid_dir)
        old_videos = [x for x in video_log_dir.glob("**/*.mkv") \
            if x.stat().st_mtime < now - self.days_old*86400]
        if old_videos:
            logger.info(f"Beginning compression of {len(old_videos)} videos")
            for video in old_videos:
                self.compress_video_logs(video)
            logger.info("Done compressing")
            print("Done compressing")
    

    # Delete compressed logs till remaining space is about 10% of total
    # drive space, if there are any compressed video files.
    # Else send an email.
    def delete_video_logs(self):
        """
        Delete files in the archive directory until at least 10% of the
        total storage is free.
        """
        # Get the value for 10% of the total storage
        stats = shutil.disk_usage(os.path.sep)
        ten_percent = stats[0] * self.fraction
        while shutil.disk_usage(os.path.sep)[2] < ten_percent:
            # Get the list of files in ascending order of date modified
            files = sorted(
                Path(self.arc_dir).glob("**/*.mp4"),
                key=os.path.getmtime
            )
            try:
                logger.info(f"Delete operation, target: {files[0]}")
                os.remove(files[0])
            except IndexError: # No files to delete
                # Send email as well; space not enough but no files to
                # delete
                self.alert()
                break

    # Compress logs older than 3 days.
    def compress_video_logs(self, video_file: Path):
        """
        Convert a video file to mp4 and compress the mp4 video.

        Parameters
        ----------
        video_file: pathlib.Path
            Path of video file to be compressed.
        """
        name, _ = os.path.basename(video_file).split(".")
        directory = os.path.dirname(video_file)
        output_file = name + ".mp4"
        output_name = os.path.join(directory, output_file)
        
        # Convert video logs to mp4
        try:
            ffmpeg.input(video_file).output(output_name)\
                .run(capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            logger.exception(f"Conversion Error: {e.stderr.decode('utf8')}")
            size_in_kb = Path(video_file).stat().st_size / 1024
            if size_in_kb < 0.6:
                logger.info(f"{video_file} is too small to compress.")
                # TO DO: remove file
                os.remove(video_file)
            return
        
        # TO DO: Remove the original video log.
        logger.info(f"Converted {video_file} -> {output_file}")
        os.remove(video_file)

        # Compress video
        dets = directory.split(os.path.sep)
        comp_path = os.path.join(self.arc_dir, *dets[-3:], output_file)
        os.makedirs(os.path.dirname(comp_path), exist_ok=True)
        res = subprocess.run(f'.{os.path.sep}ffmpeg.exe -i "{output_name}" '
            f'-vcodec libx264 -crf {self.quality} "{comp_path}"', shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if res.returncode != 0:
            # print("Compress Error:", res.stderr)
            logger.error(f"Compress Error: {res.stderr}")
            return
        # Remove the converted video log.
        logger.info(f"Compressed {output_file} -> {comp_path}")
        os.remove(output_name)
    
    def alert(self):
        """
        Get email configuration and pass to function that will send the
        email notification.
        """
        # Get sender, password, and receiver details from config file.
        try:
            sender = config["EMAIL"]["email_host_user"]
            password = config["EMAIL"]["email_host_password"]
            receiver = config["EMAIL"]["admin_email"]

            self.send_email(sender, password, receiver)
            logger.info(f"Email sent to {receiver}")
        except Exception as ex:
            logger.exception(str(ex))
    
    def send_email(self, sender: str, password: str, receiver: str):
        """
        Sends an email about the storage space left to the receiver.

        Parameters
        ----------
        sender: str
            Email address from which you want to send emails (host email).
        password: str
            Password associated with your host email account.
        receiver: str
            Receiver's email address where you want to send the alert.
        """
        ctx = ssl.create_default_context()
        message = MIMEMultipart("alternative")
        message["Subject"] = "Logger Storage Alert"
        message["From"] = sender
        message["To"] = receiver

        html, plain = self.template()

        message.attach(MIMEText(plain, "plain"))
        message.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=ctx) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, message.as_string())
    
    def template(self) -> Tuple[str, str]:
        """
        Constructs an html and plain message, either of which will be
        sent to the receiver depending on the receiver's email client
        compatibility.

        Returns
        -------
        Tuple[str, str]
            HTML message format and string/plain message format.
        """
        stats = shutil.disk_usage(os.path.sep)
        percentage_left = (stats[2]/stats[0]) * 100
        space_left = stats[2] / 1024**3
        ip = socket.gethostbyname(socket.gethostname())
        html = f"""\
                    <html>
                    <body>
                        <p>
                            The activity monitor server ({ip}) has
                            {space_left} GiB left, which is about
                            {percentage_left}%, but has no more archived video
                            logs to delete. Therefore, the operation to free
                            at least 10% of the storage was unsuccessful.
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
                \t The activity monitor server ({ip}) has {space_left} GiB 
                left, which is about {percentage_left}%, but has no more 
                archived video logs to delete. Therefore, the operation to 
                free at least 10% of the storage was unsuccessful. \n
                \t Date: {datetime.now()} \n \n
                """

        return html, plain


if __name__ == "__main__":
    logCycler = LogCycler()
    logCycler.start()

    logCycler.join()