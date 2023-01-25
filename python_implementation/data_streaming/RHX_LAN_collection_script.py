""" Script to calculate the times at which data sent to the specified LAN
directory is accessible after being written to the recording directory by the
Intan RHX software. See RHX_LAN_streaming_script.py for more details.
"""
# %% Setup
import numpy as np
import time
from datetime import datetime
import matplotlib.pyplot as plt

import RHX_realtime_reader as rhx_acq

ld = "F:/intan_streaming_test/LAN_testing"
lan_reader = rhx_acq.RHX_realtime_reader(recording_dir=ld)

# %% Get times of data accessibility in LAN directory

amp_timesteps = lan_reader.get_data_filesize()

write_len = 10000
proc_times = np.zeros(write_len)
write_count = 0
while write_count < write_len:
    temp_amp_timesteps = lan_reader.get_data_filesize()
    if temp_amp_timesteps > amp_timesteps:
        proc_times[write_count] = datetime.timestamp(datetime.now())
        amp_timesteps = temp_amp_timesteps
        write_count += 1
    else:
        time.sleep(0.001)

# %% Load in times and amounts of data writing from acquisition computer

acq_times = np.load(ld + '/open_times.npy')
acq_amounts = np.load(ld + '/write_amounts.npy')

# %% Calculate latency between writing and LAN accessibility

lat_times = proc_times - acq_times

# %% Plot latencies and amounts written

lat_times_trunc = lat_times[100:]
print(f'Average time between writes: {np.mean(lat_times_trunc)}')
print(f'Median time between writes: {np.median(lat_times_trunc)}')
print(f'Max time between writes: {np.max(lat_times_trunc)}')

plt.hist(lat_times, bins=15)
plt.show()

acq_amount_trunc = acq_amounts[100:]
print(f'Average amount written: {np.mean(acq_amount_trunc)}')
print(f'Median amount written: {np.median(acq_amount_trunc)}')
print(f'Max amount written: {np.max(acq_amount_trunc)}')

plt.hist(acq_amount_trunc, bins=15)
plt.show()
