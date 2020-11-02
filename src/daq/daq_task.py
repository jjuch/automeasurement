import nidaqmx as ndm
from nidaqmx.constants import AcquisitionType
from nidaqmx.errors import *

import matplotlib.pyplot as plt
import numpy as np
import itertools
from time import strftime, localtime
import sys
import warnings, traceback

from config.sensor import IEPE_Force_sensor, Acceleration_sensor

class DAQTask():
    def __init__(self):
        self.task = ndm.task.Task()
        self.verbose = False
        self.timestamp = strftime("%Y%m%d_%H%M%S", localtime())
        self.time_axis = []
        self.data = []
        self.error_msg = None

    def read_data(self, fs: float, measurement_time: float, plot: bool=False, verbose=False) -> bool:
        """
        Read data from task with a certain sampling frequency fs and a finite measurement time. Once finished the task is closed. A bool on successful execution is returned. A 'plot' and 'verbose' boolean are provided.
        """

        # Adapt object specific parameters
        self.verbose = verbose

        # Determine time-axis
        number_of_samples_per_channel = fs * measurement_time
        time_axis = np.linspace(0, measurement_time, number_of_samples_per_channel)
        number_of_channels = self.task.number_of_channels
        if number_of_channels is not 1:
            time_axis = list(itertools.repeat(time_axis, number_of_channels))
            time_axis = self.transpose_list_of_lists(time_axis)
        self.time_axis = time_axis

        try:
            # Set DAQ timing
            self.task.timing.cfg_samp_clk_timing(rate=fs, sample_mode=AcquisitionType.FINITE, samps_per_chan=number_of_samples_per_channel)

            # Close task when done
            self.task.register_done_event(self.close_task)

            # Read Data
            if self.verbose:
                print('Automeasurement: start reading data.')
                print('Automeasurement: fs={}Hz, time={}s'.format(fs, measurement_time))
            # raise DaqError('Test Error', 100)
            raise TypeError
            self.task.start()
            data = self.task.read(number_of_samples_per_channel=number_of_samples_per_channel, timeout=measurement_time * 1.2)
            if number_of_channels > 1:
                data = self.transpose_list_of_lists(data)
            self.data = data

        # DAQ related errors
        except DaqError as e:
            self.error_msg = traceback.format_exc()
            print("===================")
            print("DAQ related error: ")
            print("===================")
            print(self.error_msg)
            print("===================")
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                self.task.stop()
            self.close_task('Measuring error', 'error', None)
            return False

        # Other Exceptions
        except Exception as e:
            self.error_msg = traceback.format_exc()
            print("==========")
            print("Exception:")
            print("==========")
            print(self.error_msg)
            print("==========")
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                self.task.stop()
            self.close_task('Measuring error', 'error', None)
            return False
        
        if self.verbose:
            print('Automeasurement: Measurement completed.')
        
        # Simple plot of measured data
        if plot:
            plt.figure()
            plt.plot(self.time_axis, self.data)
            plt.xlabel('time (s)')
            plt.show()

        # Reset verbose
        self.verbose = False
        return True

    def close_task(self, task_handle, status, callback_data):
        if self.verbose:
            print('Automeasurement: Closing task.')
        self.task.close()
        if self.verbose:
            print("""
            Report
            ======
            task_handle: {}\n
            status: {}\n
            callback_data: {}
            """.format(task_handle, status, callback_data))
        return 0


    def export_data(self, path):
        pass


    def transpose_list_of_lists(self, list_of_lists):
        """
        Transpose a list of lists.

        Example:
        --------
            >>> in = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            >>> out = transpose_list_of_lists(in)
            >>> print(out)
                [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
        """
        return list(map(list, zip(*list_of_lists)))


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
    daq = DAQForceTask('cDAQ1Mod1/ai0:1')
    # daq.task.start()
    # plt.figure()
    # for _ in range(100):
    #     data = daq.task.read(1500)
    #     print(data)
    #     plt.plot(data)
    #     plt.pause(0.05)
    # plt.show()
    # daq.task.stop()
    # daq.task.start()
    daq.read_data(2000, 30, plot=True, verbose=True)
