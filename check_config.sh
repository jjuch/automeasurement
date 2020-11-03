#!/bin/bash

cd C:/Users/jjuchem/Documents/PhD/Services/stick_slip/automeasurement

# Path to virtual environment activation script
activate_path='ENV/Scripts/activate'
#TODO: Check if path exists, if not create

# Function calling the activation script
activate () {
    source $activate_path
}

# Check if the virtualenv is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "No VIRTUAL_ENV set"
    activate
else
    echo "VIRTUAL_ENV is set"
fi

# Run python script as module
python -m src.daq.daq_task