import nidaqmx as ndm
from nidaqmx.constants import AcquisitionType
from nidaqmx.errors import *

import matplotlib.pyplot as plt
import numpy as np
import itertools
from time import strftime, localtime, sleep
import sys, os
import warnings, traceback
import csv

from config.sensor import IEPE_Force_sensor, Acceleration_sensor
import config.mail as email_cfg
import config.measurement as measurement_cfg
from src.mail import setup_mail_client

class DAQTask():
    def __init__(self, mail_client=None, verbose=False, send_email=False):
        self.task = ndm.task.Task()
        self.verbose = verbose
        self.timestamp = strftime("%Y%m%d_%H%M%S", localtime())
        self.time_axis = None
        self.data = None
        self.error_msg = None
        self.send_email = send_email
        if mail_client is None:
            try:
                self.mail_client = setup_mail_client()
            except Exception as e:
                print('Automeasurement: Could not create a mail client.')
                # Allows to keep storing the data if the mail client fails
                self.mail_client = None
                self.send_email = False

    def __exit__(self, type, value, traceback):
        self.close()

    def read_data(self, fs: float, measurement_time: float, plot: bool=False, verbose=False, attempts=1, current_attempt=1, close_when_done: bool=True) -> bool:
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

            if close_when_done:
                # Close task when done
                self.task.register_done_event(self.close_task)

            # Print verbose info about measurement
            if self.verbose:
                print('Automeasurement: start reading data. Attempt: {}/{}'.format(current_attempt, attempts))
                print('Automeasurement: fs={}Hz, time={}s'.format(fs, measurement_time))
            
            # Remove transient from internal source
            sleep(2)

            # Testing except structure
            # if current_attempt < attempts:
            #     raise DaqError('Test Error', 100)
            # raise DaqError('Test Error', 100)
            # raise TypeError
            
            # Create new timestamp
            self.timestamp = strftime("%Y%m%d_%H%M%S", localtime())
            # The actual reading of the device
            self.task.start()
            data = self.task.read(number_of_samples_per_channel=number_of_samples_per_channel, timeout=measurement_time * 1.2)
            if number_of_channels > 1:
                data = self.transpose_list_of_lists(data)
            self.data = data

        # DAQ related errors
        except DaqError as e:
            self.error_msg = traceback.format_exc()
            print("=====================================")
            print("Automeasurement - DAQ related error: ")
            print("=====================================")
            print(self.error_msg)
            print("=====================================")
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                self.task.stop()
            if current_attempt < attempts:
                # Unregister done event
                self.task.register_done_event(None)

                # Recursive new read attempt
                recursion_bool = self.read_data(fs, measurement_time, plot=plot, verbose=verbose, attempts=attempts, current_attempt=current_attempt + 1)
                return recursion_bool
            elif current_attempt == attempts:
                if self.send_email:
                    # Send an e-mail
                    error_subject = 'NI DAQ failed to measure'
                    self.mail_client.send_error_email(self.error_msg, error_subject, email_cfg.email_from, email_cfg.email_to, email_cfg.email_cc)
                if close_when_done:
                    self.close_task('Measuring error', 'error', None)
                return False

        # Other Exceptions
        except Exception as e:
            self.error_msg = traceback.format_exc()
            print("============================")
            print("Automeasurement - Exception:")
            print("============================")
            print(self.error_msg)
            print("============================")
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                self.task.stop()
            if self.send_email:
                    # Send an e-mail
                    error_subject = 'Unexpected Exception during reading'
                    self.mail_client.send_error_email(self.error_msg, error_subject, email_cfg.email_from, email_cfg.email_to, email_cfg.email_cc)
            if close_when_done:
                self.close_task('Measuring error', 'error', None)
            return False
        
        if self.verbose:
            print('Automeasurement: Measurement completed successfully.')
        
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

    def close_mail_client(self):
        if self.verbose:
            print('Automeasurement: Closing mail client.')
        self.mail_client.quit_client()

    def close(self):
        if self.verbose:
            print('Automeasurement: Closing the DAQ Task.')

        # Catch warning that task is already closed.
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.close_task('closing', 'closing_all', None)
        self.close_mail_client()


    def export_data(self, delimiter=';', transform=False):
        """
        Export data to a csv file. The path is specified in the config/files.py file.
        The delimiter is by default ';'. The boolean 'transform' converts the data from the decimal point '.' to ','.
        """
        for i in range(len(measurement_cfg.path)):
            correct_path = measurement_cfg.path[i]
            if measurement_cfg.path[i][-2:-1] != "\\":
                correct_path = correct_path + "\\"
            
            # Check if path exists
            if not os.path.exists(correct_path + 'data'):
                os.makedirs(correct_path + 'data')

            # Set path with data name
            nameCSV = correct_path + "data\\data_" + self.timestamp + ".csv"
            
            try:
                #Write to CSV
                with open(nameCSV, 'w', newline='') as csvfile:
                    dataWriter = csv.writer(csvfile, delimiter=';', quotechar='|',quoting=csv.QUOTE_NONE)

                    if self.time_axis is not None:
                        for i in range(len(self.time_axis)):
                            row = []
                            # change '.' into ','
                            for j in range(len(self.time_axis[0])):
                                if transform:
                                    row.append(self._localizeFloats(self.time_axis[i][j])) 
                                    row.append(self._localizeFloats(self.data[i][j]))
                                else:
                                    row.append(self.time_axis[i][j])
                                    row.append(self.data[i][j])
                            dataWriter.writerow(row)

                        # decimal point: '.'
                        # dataWriter.writerow([self.time_axis[i],self.data[i]])
                    csvfile.close()
            # except FileNotFoundError:
            #     print("Automeasurement: The path in the config/files.py does not exist. Please provide an existing path.")
            except Exception as e:
                self.error_msg = traceback.format_exc()
                self.error_msg = self.error_msg + "\nPath: {}".format(correct_path)
                print("============================")
                print("Automeasurement - Exception:")
                print("============================")
                print(self.error_msg)
                print("============================")
                if self.send_email:
                        # Send an e-mail
                        error_subject = 'Unexpected Exception during saving data'
                        self.mail_client.send_error_email(self.error_msg, error_subject, email_cfg.email_from, email_cfg.email_to, email_cfg.email_cc)


    
    def _localizeFloats(self,el):
        return str(el).replace('.', ',') if isinstance(el, float) else el


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
    def __init__(self, channel_names, mail_client=None, verbose=False, send_email=False):
        super().__init__(mail_client=mail_client, verbose=verbose, send_email=send_email)
        try:
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
        except Exception as e:
            self.error_msg = traceback.format_exc()
            print("============================")
            print("Automeasurement - Exception:")
            print("============================")
            print(self.error_msg)
            print("============================")
            if self.send_email:
                # Send an e-mail
                error_subject = 'Unexpected Exception during creation of task'
                self.mail_client.send_error_email(self.error_msg, error_subject, email_cfg.email_from, email_cfg.email_to, email_cfg.email_cc)
            self.close()


class DAQAccelerationTask(DAQTask):
    def __init__(self, channel_names, mail_client=None, verbose=False, send_email=False):
        super().__init__(mail_client=mail_client, verbose=verbose, send_email=send_email)
        try:
            self.task.ai_channels.add_ai_accel_chan(channel_names,
                terminal_config=Acceleration_sensor['terminal_config'],
                min_val=Acceleration_sensor['min_val'],
                max_val= Acceleration_sensor['max_val'],
                units=Acceleration_sensor['units'],
                sensitivity=Acceleration_sensor['sensitivity'],
                sensitivity_units=Acceleration_sensor['sensitivity_units'],
                current_excit_source=Acceleration_sensor['current_excit_source'],
                current_excit_val=Acceleration_sensor['current_excit_val'])
        except Exception as e:
            self.error_msg = traceback.format_exc()
            print("============================")
            print("Automeasurement - Exception:")
            print("============================")
            print(self.error_msg)
            print("============================")
            if self.send_email:
                # Send an e-mail
                error_subject = 'Unexpected Exception during creation of task'
                self.mail_client.send_error_email(self.error_msg, error_subject, email_cfg.email_from, email_cfg.email_to, email_cfg.email_cc)
            self.close()



if __name__ == "__main__":
    # task = DAQTask('cDAQ1/ai0:3')
    # daq = DAQForceTask('cDAQ1Mod1/ai0:1')
    daq = DAQAccelerationTask('cDAQ1Mod1/ai0:3', verbose=True, send_email=True)
    # success = daq.read_data(2000, 5, plot=False, verbose=True, attempts=2)
    # if success:
    #     daq.export_data()
    # daq.close()
