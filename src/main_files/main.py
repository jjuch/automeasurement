from src.daq.daq_task import DAQAccelerationTask

import config.measurement as cfg_meas
import config.sensor as cfg_sensor

# Configure task
daq = DAQAccelerationTask(cfg_sensor.channel_names, verbose=True, send_email=True)

# Measure data
read_success = daq.read_data(cfg_meas.measurement_frequency, cfg_meas.measurement_time, plot=False, attempts=cfg_meas.attempts, close_when_done=False)

# Save data
if read_success:
    daq.export_data(cfg_meas.path)

# Close all resources
daq.close()