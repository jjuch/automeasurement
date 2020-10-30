from src.mail.mail_client import MailClient

import config.secrets as cfg


mc = MailClient(cfg.host, cfg.port, cfg.user, cfg.password)
mc.send_test(cfg.email_from, cfg.email_to, cc_email=cfg.email_cc)
mc.quit_client()