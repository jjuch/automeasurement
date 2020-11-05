from nidaqmx.constants import (AccelUnits, AccelSensitivityUnits, AcquisitionType, ExcitationDCorAC, ExcitationSource, ForceIEPESensorSensitivityUnits, ForceUnits, TerminalConfiguration, UsageTypeAI)

channel_names = "cDAQ1Mod1/ai0:3, cDAQ1Mod2/ai0"

# IEPE Force sensor
IEPE_Force_sensor = {
    'terminal_config' : TerminalConfiguration.PSEUDODIFFERENTIAL,
    'min_val' : -50,
    'max_val' : 50,
    'units' : ForceUnits.NEWTONS,
    'sensitivity' : 10.99,
    'sensitivity_units' : ForceIEPESensorSensitivityUnits.M_VOLTS_PER_NEWTON,
    'current_excit_source' : ExcitationSource.INTERNAL,
    'current_excit_val' : 0.002
}

#Acceleration sensor
Acceleration_sensor = {
    'terminal_config' : TerminalConfiguration.PSEUDODIFFERENTIAL,
    'min_val' : -30,
    'max_val' : 30,
    'units' : AccelUnits.G,
    'sensitivity' : 100,
    'sensitivity_units' : AccelSensitivityUnits.M_VOLTS_PER_G,
    'current_excit_source' : ExcitationSource.INTERNAL,
    'current_excit_val' : 0.002
}
