class SmtpClient:
    def __init__(self, server):
        self.server = server

    def send(self, recipient, message):
        # ... send logic

# Refactored
class AlertService:
    def __init__(self, smtp_client):
        self.smtp = smtp_client

    def send_alert(self, user_email, message):
        self.smtp.send(user_email, message)
