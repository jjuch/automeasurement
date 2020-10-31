import nidaqmx as ndm
from nidaqmx.constants import (AccelUnits, AccelSensitivityUnits, AcquisitionType, ExcitationDCorAC, ExcitationSource, ForceIEPESensorSensitivityUnits, ForceUnits, TerminalConfiguration, UsageTypeAI)
import matplotlib.pyplot as plt
from automeasurement.config.sensor import IEPE_Force_sensor, Acceleration_sensor

class DAQTask():
    def __init__(self):
        self.task = ndm.task.Task()


class DAQForceTask(DAQTask):
    def __init__(self, channel_names):
        super().__init__()
        self.task.ai_channels.add_ai_force_iepe_chan(channel_names,
            terminal_config=IEPE_Force_sensor['terminal_config'],
            min_val=IEPE_Force_sensor['min_val'],
            max_val=IEPE_Force_sensor['max_val'],
            units=IEPE_Force_sensor['units'],
            sensitivity=IEPE_Force_sensor['sensitivity'],
            sensitivity_units=IEPE_Force_sensor['sensitivity_units'],
            current_excit_source=IEPE_Force_sensor['current_excit_source'],
            current_excit_val=IEPE_Force_sensor['current_excit_val'])
        self.task.timing.cfg_samp_clk_timing(1000, sample_mode=AcquisitionType.CONTINUOUS)
        # print(self.task.channels.ai_meas_type)


class DAQAccelerationTask(DAQTask):
    def __init__(self, channel_names):
        super().__init__()
        self.task.ai_channels.add_ai_accel_chan(channel_names,
            terminal_config=Acceleration_sensor['terminal_config'],
            min_val=Acceleration_sensor['min_val'],
            max_val= Acceleration_sensor['max_val'],
            units=Acceleration_sensor['units'],
            sensitivity=Acceleration_sensor['sensitivity'],
            sensitivity_units=Acceleration_sensor['sensitivity_units'],
            current_excit_source=Acceleration_sensor['current_excit_source'],
            current_excit_val=Acceleration_sensor['current_excit_val'])



if __name__ == "__main__":
    # task = DAQTask('cDAQ1/ai0:3')
    daq = DAQTask('cDAQ1Mod1/ai0')
    daq.task.start()
    plt.figure()
    for _ in range(1000):
        data = daq.task.read(1500)
        print(data)
        plt.plot(data)
        plt.pause(0.05)
    plt.show()
    daq.task.stop()
