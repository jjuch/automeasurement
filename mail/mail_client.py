from smtplib import SMTP_SSL

class MailClient():
    def __init__(self, host, port, user, pswd):
        self.server = SMTP_SSL(host=host, port=port)
        self.server.set_debuglevel(1)
        self.server.login(user, pswd)

    def send_test(self, from_email, to_email):
        msg = ("From: %s\r\nTo: %s\r\n\r\n" % (from_email, ", ".join(to_email)))
        msg = msg + 'This is a test.'
        self.server.sendmail(from_email, to_email, msg)

    def quit_server(self):
        self.server.quit()
