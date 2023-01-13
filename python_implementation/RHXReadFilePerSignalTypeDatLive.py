"""Conversion and modification of 'RHXReadFilePerSignalTypeDatLive.m' included
in the Intan streaming tutorial to Python script suitable for acquisition of
neural data from intra-op cases for the Cogan/Viventi Lab at Duke University.

Author: Zac Spalding
"""

# %%

# np.fromfile in place of fread from matlab
# (https://stackoverflow.com/questions/2146031/what-is-the-equivalent-of-fread-from-matlab-in-python)
import numpy as np
import matplotlib.pyplot as plt
import os
import keyboard
import time
import tkinter as tk
from tkinter import filedialog

from load_intan_rhd_format.load_intan_rhd_format import read_data


MICROV_CONV = 0.195
CHUNK_SIZE = 30000


def get_recording_dir():
    # hide tk window
    root=tk.Tk()
    root.attributes("-alpha", 0)

    recording_dir = filedialog.askdirectory() # get recording directory
    root.destroy()

    return recording_dir


def read_info_rhd_wrapper(recording_dir):
    info_path = recording_dir + '/info.rhd'
    fileinfo = read_data(info_path)
    return fileinfo
        

def read_timestamp(ts_fid, fileinfo, offset=0):
    # ts_path = recording_dir + '/time.dat'
    # num_samples = int(os.path.getsize(ts_path) / 4) # int32 = 4 bytes
    # with open(ts_path, 'rb') as fid:
    ts = np.fromfile(ts_fid, count=CHUNK_SIZE, offset=offset, dtype=np.int32)
    ts = ts / fileinfo['frequency_parameters']['amplifier_sample_rate']
    return ts


def read_amp_data(amp_fid, fileinfo, offset=0):
    # data_path = recording_dir + '/amplifier.dat'
    num_chan = len(fileinfo['amplifier_channels'])
    # num_samples = int(os.path.getsize(data_path) / (2 * num_chan)) # int16 = 2 bytes
    # with open(data_path, 'rb') as fid:
    d = np.fromfile(amp_fid, count=CHUNK_SIZE*num_chan, offset=offset, dtype=np.int16).reshape(-1, num_chan).T
    d = d * MICROV_CONV
    return d

# %%

rd = "F:\intan_streaming_test\data_save_testing"
fileinfo = read_info_rhd_wrapper(rd)

ts_path = rd + '/time.dat'
with open(ts_path, 'rb') as ts_id:
    ts = read_timestamp(ts_id, fileinfo)

amp_path = rd + '/amplifier.dat'
with open(amp_path, 'rb') as amp_id:
    amp_data = read_amp_data(amp_id, fileinfo)

# %%
plt.plot(ts, amp_data[0,:].T)
plt.show()

# %%

rd = "F:\intan_streaming_test\data_save_testing"
fileinfo = read_info_rhd_wrapper(rd)
num_chan = len(fileinfo['amplifier_channels'])

ts_path = rd + '/time.dat'
ts_fid = open(ts_path, 'rb')

amp_path = rd + '/amplifier.dat'
amp_fid = open(amp_path, 'rb')

plotted_samples = 0

plt.ion()

fig = plt.figure()
ax = fig.add_subplot(111)
amp_plot, = ax.plot([], [], 'r-') # Returns a tuple of line objects, thus the comma
ax.set_ylim([-1000, 1000])
ax.set_xlim([0, 1])


while True:
    ts_size = int(os.path.getsize(ts_path) / 4) # int32 = 4 bytes
    amp_size = int(os.path.getsize(amp_path) / (2 * num_chan)) # int16 = 2 bytes

    if min(ts_size, amp_size) - plotted_samples >= CHUNK_SIZE:
        ts = read_timestamp(ts_fid, fileinfo)
        amp_data = read_amp_data(amp_fid, fileinfo)

        amp_plot.set_data(ts, amp_data[0,:])
        ax.set_xlim(ts[0], ts[-1])

        fig.canvas.draw()
        fig.canvas.flush_events()
        plotted_samples += CHUNK_SIZE
    else:
        print('waiting for data')
        time.sleep(0.01)






