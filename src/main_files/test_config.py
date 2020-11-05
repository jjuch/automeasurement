from src.daq.daq_task import DAQTask
from src.mail.mail_client import MailClient

#######
### Test mail client
import config.mail as cfg_mail

if type(cfg_mail.email_from) is not str:
    raise ValueError("[config/mail] email_from should be a string.")
if type(cfg_mail.email_to) is not list:
    raise ValueError("[config/mail] email_to should be a list of strings.")
if type(cfg_mail.email_cc) is not list:
    raise ValueError("[config/mail] email_cc should be a list of strings.")

import config.secrets as cfg_scr
mc = MailClient(cfg_scr.host, cfg_scr.port, cfg_scr.user, cfg_scr.password)

# Send a test mail
mc.send_test_email(cfg_mail.email_from, cfg_mail.email_to, cc_email=cfg_mail.email_cc)

# Clean up socket
mc.quit_client()


##############################
### Test DAQ task

import config.measurement as cfg_meas
daq = DAQTask(verbose=True, send_email=True)
# Test export paths
daq.export_data(cfg_meas.path)
# Close resources
daq.close()