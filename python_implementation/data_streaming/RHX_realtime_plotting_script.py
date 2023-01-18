# %%
# imports
import matplotlib.pyplot as plt
import numpy as np
import time
import os

import RHX_realtime_reader as rhx_acq

rd = "F:/intan_streaming_test/data_save_testing"
realtime_reader = rhx_acq.RHX_realtime_reader(recording_dir=rd, chunk_len=0.5)


# %% Plot current data from first channel

# ts, amp_data = realtime_reader.current_acquire(plot=True)
# print(ts.shape, amp_data.shape)

# %% Plot continuously updating data

plt.ion()
realtime_reader.realtime_acquire(plot=True)

# # amp_fid = open(realtime_reader.lowpass_path, 'rb')
# amp_path = rd + '/amplifier.dat'
# amp_fid = open(amp_path, 'rb')
# ts_path = rd + '/time.dat'
# ts_fid = open(ts_path, 'rb')

# fileinfo = rhx_acq.read_info_rhd_wrapper(rd + '/info.rhd')
# num_chan = len(fileinfo['amplifier_channels'])
# fs = fileinfo['frequency_parameters']['amplifier_sample_rate']

# plotted_samples = 0

# plt.ion()

# fig = plt.figure()
# ax = fig.add_subplot(111)
# amp_plot, = ax.plot([], [], 'r-')
# ax.set_ylim([-1000, 1000])
# ax.set_xlim([0, 1])

# count = 0
# while True:
#     ts_size = int(os.path.getsize(ts_path) / 4)
#     amp_size = int(os.path.getsize(amp_path) / (2 * num_chan))
#     # update_size = int(realtime_reader.chunk_len * realtime_reader.fs_down)
#     update_size = int(rhx_acq.CHUNK_LENGTH * fs)

#     if min(ts_size, amp_size) - plotted_samples >= update_size:
#         ts = rhx_acq.read_timestamp(ts_fid, fs)
#         # amp_data = realtime_reader.read_amp_data(amp_fid, read_all=False)
#         amp_data = rhx_acq.read_amp_data(amp_fid, num_chan,
#                                          fs)
#         # ts = realtime_reader.create_timestamp_amp(amp_data.shape[1],
#         #                                           start=plotted_samples)

#         amp_plot.set_data(ts, amp_data[0, :])
#         ax.set_xlim(ts[0], ts[-1])

#         fig.canvas.draw()
#         fig.canvas.flush_events()
#         plotted_samples += update_size
#     else:
#         if count % 100 == 1:
#             print('Waiting for data...')
#         if count >= 1000:
#             print('Timed out. Check that the Intan '
#                   'software is still recording data.')
#             break
#         time.sleep(0.01)
#         count += 1

# amp_fid.close()
