import yaml
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import requests

# Load credentials from YAML file
with open("/app/cronchoco/credentials.yml", 'r') as stream:
    try:
        credentials = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

smtp_port = credentials['smtp_port']
smtp_server = credentials['smtp_server']
sender_mail = credentials['sender_mail']
sender_pw = credentials['sender_pw']
recipients = credentials['recipients']


def send_alert(title, message_body):
    message = MIMEMultipart("alternative")
    message["Subject"] = f"{title}"
    message["From"] = sender_mail
    message["To"] = ", ".join(recipients)
    body = f"{message_body}"
    message.attach(MIMEText(body, "html"))
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls(context=context)
        server.login(sender_mail, sender_pw)
        server.sendmail(sender_mail, recipients, message.as_string())


def check_if_live():


    with open("/app/tools/chocolateyinstall.ps1", "r") as file:
        lines = file.readlines()
    for i, line in enumerate(lines):
        if "$url        =" in line:
            actual_url = line.split('=', 1)[-1].strip().strip('\'"')
            # actual_url = 'https://gitlab.com/openconnect/openconnect/-/jobs/5809119325/artifacts/download?file_type=archive'
            print(actual_url)
            if requests.get(actual_url).status_code == 404:
                send_alert("OpenConnect Chocolatey Package is Down", "sorry bro")
            elif requests.get(actual_url).status_code == 200:
                print(":)")


if __name__ == "__main__":
    print(f"Running script at {datetime.now()}")
    # send_alert("This message is sent every 30 minutes", "<h1>AMONGUS!!!!</h1>")
    check_if_live()
    # print(requests.get("https://gitlab.com/openconnect/openconnect/-/jobs/5809119325/artifacts/download?file_type=archive").status_code)