# automeasurement
An automatic measuring and logging protocol


## Install (Windows)
### Prerequisites
* git (in terminal)
* python (in terminal)
* virtualenv
* NI drivers

### Procedure
1. Create a folder
2. Open 'cmd' and navigate to the folder
3. Clone this repo in the folder
```
    >>> git clone https://github.ugent.be/DySC-SYSTeMS/automeasurement.git
```
4. Run the setup
```
    >>> cd automeasurement
    >>> setup.bat
```
5. Change config files

6. Validate the config file by running the `check_config.bat` file
```
    >>> check_config.bat
```
Check your mail account if all recepients received two mails. The first one indicates that the mail configuration is successfull. The second one indicates that the export paths are ok. A file will be saved at the location. **Remove these files as they do not contain any relevant info.** 

## Run Automeasurement
Now, everything is ready to use the automeasurement protocol. You can use the `main.bat` file to do a measurement. To have repetitive measurments, the Task Scheduler of windows can be used. 

**Important:** Add the absolute path of the `main.bat` file to the `Start in` field and refer to the main.bat file without path.
