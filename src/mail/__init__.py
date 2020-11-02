from src.mail.mail_client import MailClient

import config.secrets as cfg_scr

def setup_mail_client():
    return MailClient(cfg_scr.host, cfg_scr.port, cfg_scr.user, cfg_scr.password)