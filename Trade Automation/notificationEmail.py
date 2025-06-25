import smtplib
from email.message import EmailMessage

class EmailSender:
    def __init__(self, gmail_address):
        self.gmail_address = gmail_address
        self.app_password = 'fpgz jjwi unvu wijg'

    def send_gmail(self, recipient, subject, body):
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = self.gmail_address
        msg["To"] = recipient

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(self.gmail_address, self.app_password)
                smtp.send_message(msg)

            print(f"Email sent to {recipient}")
        except Exception as e:
            print("Idk man something went wrong in email, not smart enough to include errors")

# Example usage
GMAIL_ADDRESS = "your_email@gmail.com"
APP_PASSWORD = "your_app_password"

email_sender = EmailSender(GMAIL_ADDRESS, APP_PASSWORD)

recipient = input("Input recipient: ")
subject = "Hello from Python + Gmail"
body = "This is a simple plaintext email sent via Gmail SMTP and a Python script."

email_sender.send_gmail('noelalex449@gmail.com', subject, body)