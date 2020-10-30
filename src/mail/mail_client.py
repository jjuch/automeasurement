from smtplib import SMTP_SSL
from email.message import EmailMessage

class MailClient():
    def __init__(self, host, port, user, pswd):
        self.client = SMTP_SSL(host=host, port=port)
        self.client.set_debuglevel(1)
        self.client.login(user, pswd)

    def send_test(self, from_email, to_email, cc_email=None):
        """
        Send a test mail with the current server.
        """
        
        # Create Email Message instance with header
        msg = EmailMessage()
        msg['Subject'] = '[Measurements.dysc] testprotocol'
        msg['From'] = from_email
        msg['To'] = to_email
        all_to_email = to_email
        if cc_email is not None:
            msg['Cc'] = cc_email
            all_to_email = all_to_email + cc_email

        # Add body to email
        txt = ("From: %s\r\nTo: %s\r\n\r\n" % (from_email, ", ".join(to_email)))
        txt = txt + "This is a test.\r\n\r\nDisclaimer: this mail is sent using a Python SMTP_SSL client. If you no longer want to receive this e-mail, send a reply to 'measurements.dysc@UGent.be'."
        msg.set_content(txt)
        
        # Send mail with client
        self.client.sendmail(from_email, all_to_email, msg.as_string())

    def quit_client(self):
        self.client.quit()