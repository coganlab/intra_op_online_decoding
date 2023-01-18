"""Conversion and modification of 'RHXReadFilePerSignalTypeDatLive.m' included
in the Intan streaming tutorial to Python script suitable for acquisition of
neural data from intra-op cases for the Cogan/Viventi Lab at Duke University.

Author: Zac Spalding
"""

# np.fromfile in place of fread from matlab
# (https://stackoverflow.com/questions/2146031/what-is-the-equivalent-of-fread-from-matlab-in-python)
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog
import xml.etree.ElementTree as ET

from load_intan_rhd_format.load_intan_rhd_format import read_data

MICROV_CONV = 0.195
CHUNK_LENGTH = 1  # second(s)


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


def get_downrate_from_settings(recording_dir):
    settings_path = recording_dir + '/settings.xml'
    if os.path.exists(settings_path):
        tree = ET.parse(settings_path)
        gen_config = [x for x in tree.iter() if x.tag == 'GeneralConfig']
        if len(gen_config) > 0:
            gen_config = gen_config[0]
            if 'LowpassWaveformDownsampleRate' in gen_config.attrib:
                return int(gen_config.attrib['LowpassWaveformDownsampleRate'])
    return False


def read_timestamp(ts_fid, fs, offset=0):
    # ts_path = recording_dir + '/time.dat'
    # num_samples = get_timestamp_filesize(ts_path)
    # with open(ts_path, 'rb') as fid:
    ts = np.fromfile(ts_fid, count=int(CHUNK_LENGTH*fs), offset=offset,
                     dtype=np.int32)
    ts = ts / fs
    return ts


def read_amp_data(amp_fid, fileinfo, fs, offset=0):
    # data_path = recording_dir + '/amplifier.dat'
    num_chan = len(fileinfo['amplifier_channels'])
    # num_samples = get_data_filesize(data_path, num_chan)
    # with open(data_path, 'rb') as fid:
    d = np.fromfile(amp_fid, count=int(CHUNK_LENGTH*fs*num_chan),
                    offset=offset, dtype=np.int16).reshape(-1, num_chan).T
    d = d * MICROV_CONV
    return d

# commented out as we want to save 30 kHz data from intan - not downsample
# directly from intan RHX
# def acquire_data(recording_dir):
#     # read rhd file header
#     fileinfo = read_info_rhd_wrapper(recording_dir)
#     fs = fileinfo['frequency_parameters']['amplifier_sample_rate']

#     # look for downsampled rate in settings.xml
#     lowpass = False
#     downrate = get_downrate_from_settings(recording_dir)
#     if downrate is not False:
#         print('Downsampled by factor of {}. New rate: {} Hz'.format(downrate,
#               int(fs / downrate)))
#         fs = int(fs / downrate)
#         lowpass = True
#     else:
#         print('No downsampled rate found in settings.xml. '
#               'Using original rate.')

#     # open timestamp file
#     ts_path = recording_dir + '/time.dat'
#     ts_id = open(ts_path, 'rb')

#     # open correct data file (amplifier or lowpass) depending on settings
#     if lowpass:
#         data_path = recording_dir + '/lowpass.dat'
#     else:
#         data_path = recording_dir + '/amplifier.dat'
#     data_id = open(data_path, 'rb')

#     # read timestamp and amplifier data
#     ts = read_timestamp(ts_id, fs)
#     amp_data = read_amp_data(data_id, fileinfo, fs)

#     ts_id.close()
#     data_id.close()

#     return ts, amp_data
