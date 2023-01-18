# %%
# imports
import matplotlib.pyplot as plt
import numpy as np
import time
import os
import xml.etree.ElementTree as ET

import RHX_realtime_reader as rhx_acq

rd = "F:/intan_streaming_test/data_save_testing"


# %% Plot single chunk of data for first channel

ts, amp_data = rhx_acq.acquire_data(rd)
print(ts.shape, amp_data.shape)

plt.plot(ts, amp_data[0, :].T)
plt.show()

# %% Determine write interval

fileinfo = rhx_acq.read_info_rhd_wrapper(rd)
num_chan = len(fileinfo['amplifier_channels'])
ts_path = rd + '/time.dat'
amp_path = rd + '/amplifier.dat'

amp_size = rhx_acq.get_data_filesize(amp_path, num_chan)

write_len = 10000
write_times = np.zeros(write_len)
write_amount = np.zeros(write_len)
write_count = 0
start = time.time()
while write_count < write_len:
    temp_amp_size = rhx_acq.get_data_filesize(amp_path, num_chan)
    if temp_amp_size > amp_size:
        write_times[write_count] = time.time() - start
        write_amount[write_count] = temp_amp_size - amp_size
        start = time.time()
        amp_size = temp_amp_size
        write_count += 1
    else:
        time.sleep(0.001)

write_times = write_times[100:]
print(f'Average time between writes: {np.mean(write_times)}')
print(f'Median time between writes: {np.median(write_times)}')
print(f'Max time between writes: {np.max(write_times)}')

plt.hist(write_times, bins=15)
plt.show()

write_amount = write_amount[100:]
print(f'Average amount written: {np.mean(write_amount)}')
print(f'Median amount written: {np.median(write_amount)}')
print(f'Max amount written: {np.max(write_amount)}')

plt.hist(write_amount, bins=15)
plt.show()


# %% Plot continuously updating data

rd = "F:/intan_streaming_test/data_save_testing"
fileinfo = rhx_acq.read_info_rhd_wrapper(rd)
num_chan = len(fileinfo['amplifier_channels'])

ts_path = rd + '/time.dat'
ts_fid = open(ts_path, 'rb')

amp_path = rd + '/amplifier.dat'
amp_fid = open(amp_path, 'rb')

plotted_samples = 0

plt.ion()

fig = plt.figure()
ax = fig.add_subplot(111)
amp_plot, = ax.plot([], [], 'r-')
ax.set_ylim([-1000, 1000])
ax.set_xlim([0, 1])

count = 0
while True:
    ts_size = int(os.path.getsize(ts_path) / 4)
    amp_size = int(os.path.getsize(amp_path) / (2 * num_chan))

    if min(ts_size, amp_size) - plotted_samples >= rhx_acq.CHUNK_SIZE:
        ts = rhx_acq.read_timestamp(ts_fid, fileinfo)
        amp_data = rhx_acq.read_amp_data(amp_fid, fileinfo)

        amp_plot.set_data(ts, amp_data[0, :])
        ax.set_xlim(ts[0], ts[-1])

        fig.canvas.draw()
        fig.canvas.flush_events()
        plotted_samples += rhx_acq.CHUNK_SIZE
    else:
        print('waiting for data')
        if count == 1000:
            break
        time.sleep(0.01)
        count += 1

ts_fid.close()
amp_fid.close()
