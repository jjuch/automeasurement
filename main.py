from mail.mail_client import MailClient

import config.secrets as cfg


mc = MailClient(cfg.host, cfg.port, cfg.user, cfg.password)
mc.send_test(cfg.email_from, cfg.email_to)