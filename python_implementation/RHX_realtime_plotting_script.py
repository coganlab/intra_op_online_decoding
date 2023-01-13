# imports
import matplotlib as plt
import time
import os

import RHXAcquisitionFilePerSignalType as rhx_acq

# %% Plot single chunk of data for first channel

rd = "F:/intan_streaming_test/data_save_testing"
fileinfo = rhx_acq.read_info_rhd_wrapper(rd)

ts_path = rd + '/time.dat'
with open(ts_path, 'rb') as ts_id:
    ts = rhx_acq.read_timestamp(ts_id, fileinfo)

amp_path = rd + '/amplifier.dat'
with open(amp_path, 'rb') as amp_id:
    amp_data = rhx_acq.read_amp_data(amp_id, fileinfo)

plt.plot(ts, amp_data[0, :].T)
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
