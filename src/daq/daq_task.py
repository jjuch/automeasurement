import nidaqmx as ndm
from nidaqmx.constants import (AcquisitionType, ExcitationDCorAC, ExcitationSource, ForceIEPESensorSensitivityUnits, ForceUnits, TerminalConfiguration, UsageTypeAI)
import matplotlib.pyplot as plt


class DAQTask():
    def __init__(self, channel_names):
        self.task = ndm.task.Task()
        self.task.ai_channels.add_ai_force_iepe_chan(channel_names,\
            terminal_config=TerminalConfiguration.PSEUDODIFFERENTIAL,\
            min_val=-50,\
            max_val=50,\
            units=ForceUnits.NEWTONS,\
            sensitivity=10.99,\
            sensitivity_units=ForceIEPESensorSensitivityUnits.M_VOLTS_PER_NEWTON,\
            current_excit_source=ExcitationSource.INTERNAL,\
            current_excit_val=0.002)
        self.task.timing.cfg_samp_clk_timing(1000, sample_mode=AcquisitionType.CONTINUOUS)
        print(self.task.channels.ai_meas_type)


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
