"""Conversion and modification of 'RHXReadFilePerSignalTypeDatLive.m' included
in the Intan streaming tutorial to Python script suitable for acquisition of
neural data from intra-op cases for the Cogan/Viventi Lab at Duke University.

Author: Zac Spalding
"""

# np.fromfile in place of fread from matlab
# (https://stackoverflow.com/questions/2146031/what-is-the-equivalent-of-fread-from-matlab-in-python)
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import tkinter as tk
from tkinter import filedialog

from load_intan_rhd_format.load_intan_rhd_format import read_data


MICROV_CONV = 0.195
CHUNK_SIZE = 30000


def get_recording_dir():
    # hide tk window
    root = tk.Tk()
    root.attributes("-alpha", 0)

    recording_dir = filedialog.askdirectory()  # get recording directory
    root.destroy()

    return recording_dir


def get_timestamp_filesize(ts_path):
    return int(os.path.getsize(ts_path) / 4)  # int32 = 4 bytes


def get_data_filesize(data_path, num_chan):
    return int(os.path.getsize(data_path) / (2 * num_chan))  # int16 = 2 bytes


def read_info_rhd_wrapper(recording_dir, verbose=True):
    info_path = recording_dir + '/info.rhd'
    fileinfo = read_data(info_path, verbose=verbose)
    return fileinfo


def read_timestamp(ts_fid, fileinfo, offset=0):
    # ts_path = recording_dir + '/time.dat'
    # num_samples = get_timestamp_filesize(ts_path)
    # with open(ts_path, 'rb') as fid:
    ts = np.fromfile(ts_fid, count=CHUNK_SIZE, offset=offset, dtype=np.int32)
    ts = ts / fileinfo['frequency_parameters']['amplifier_sample_rate']
    return ts


def read_amp_data(amp_fid, fileinfo, offset=0):
    # data_path = recording_dir + '/amplifier.dat'
    num_chan = len(fileinfo['amplifier_channels'])
    # num_samples = get_data_filesize(data_path, num_chan)
    # with open(data_path, 'rb') as fid:
    d = np.fromfile(amp_fid, count=CHUNK_SIZE*num_chan, offset=offset,
                    dtype=np.int16).reshape(-1, num_chan).T
    d = d * MICROV_CONV
    return d
