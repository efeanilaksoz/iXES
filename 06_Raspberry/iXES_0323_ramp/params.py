from time import time
import numpy as np

# GLOBAL VARIABLES ***************************************************************

# Characteristics
FORCE_UUID = "7F510019-1B15-11E5-B60B-1697F925EC7B" #  notify firmware >= 14
BATTERY_UUID = "00002a19-0000-1000-8000-00805f9b34fb" # read

# Filenames
BINFILES = ["binary_la", "binary_ll","binary_ra","binary_rl"]

# Recording duration & Sampling Frequency
REF_TIME = time()
