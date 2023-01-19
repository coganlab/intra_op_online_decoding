"""Conversion and modification of 'RHXReadFilePerSignalTypeDatLive.m' included
in the Intan streaming tutorial to Python script suitable for acquisition of
neural data from intra-op cases for the Cogan/Viventi Lab at Duke University.

Author: Zac Spalding
"""

# np.fromfile in place of fread from matlab
# (https://stackoverflow.com/questions/2146031/what-is-the-equivalent-of-fread-from-matlab-in-python)
import numpy as np
import matplotlib.pyplot as plt
import time
import os
import tkinter as tk
from tkinter import filedialog
import xml.etree.ElementTree as ET

from .load_intan_rhd_format.load_intan_rhd_format import read_data

MICROV_CONV = 0.195
CHUNK_LENGTH = 1  # second(s)


class RHX_realtime_reader():
    def __init__(self, recording_dir=None, chunk_len=1, verbosity=True):

        self.MICROV_CONV = 0.195
        self.chunk_len = chunk_len
        self.verbosity = verbosity

        if recording_dir is None:
            try:
                recording_dir = get_recording_dir()
            except FileNotFoundError:
                print("No recording directory found. Please select one.")
        self.recording_dir = recording_dir

        # self.info_path = self.recording_dir + '/info.rhd'
        # self.settings_path = self.recording_dir + '/settings.xml'
        self.ts_path = self.recording_dir + '/time.dat'
        self.amp_path = self.recording_dir + '/amplifier.dat'
        self.lowpass_path = self.recording_dir + '/lowpass.dat'

        self.get_fileinfo(verbose=self.verbosity)
        self.read_settings()

    def get_fileinfo(self, verbose=True):
        fileinfo = read_info_rhd_wrapper(self.recording_dir, verbose=verbose)
        self.fileinfo = fileinfo
        self.fs = fileinfo['frequency_parameters']['amplifier_sample_rate']
        self.num_chan = len(fileinfo['amplifier_channels'])

    def read_settings(self):
        settings_etree = parse_settings(self.recording_dir)
        if settings_etree is not False:
            downrate = get_downrate_from_settings(settings_etree)
            if downrate is not False:
                self.fs_down = int(self.fs / downrate)

    def get_timestamp_filesize(self):
        return int(os.path.getsize(self.ts_path) / 4)  # int32 = 4 bytes

    def get_data_filesize(self):
        return int(os.path.getsize(self.lowpass_path) /
                   (2 * self.num_chan))  # int16 = 2 bytes

    def create_timestamp_lp(self, num_samples, start=0):
        ts = np.arange(start, start + num_samples) / self.fs_down
        return ts

    def read_amp_data(self, data_fid, read_all=False):
        if read_all:
            read_len = -1
        else:
            read_len = int(self.chunk_len * self.fs_down * self.num_chan)

        d = np.fromfile(data_fid, count=read_len,
                        dtype=np.int16).reshape(-1, self.num_chan).T
        d = d * self.MICROV_CONV
        return d

    def acquire_current(self, plot=False):
        ts_fid = open(self.ts_path, 'rb')
        data_fid = open(self.lowpass_path, 'rb')

        # read timestamp and amplifier data
        amp_data = self.read_amp_data(data_fid, read_all=True)
        ts = self.create_timestamp_lp(amp_data.shape[1])

        ts_fid.close()
        data_fid.close()

        if plot:
            plt.figure()
            plt.plot(ts, amp_data[0:5, :].T)
            plt.ylabel('Voltage (uV)')
            plt.xlabel('Time (s)')
            plt.show()

        return ts, amp_data

    def acquire_realtime(self, plot=False):
        data_fid = open(self.lowpass_path, 'rb')

        if plot:
            plotted_samples = 0

            plt.ion()
            fig = plt.figure()
            ax = fig.add_subplot(111)
            amp_plot, = ax.plot([], [], 'r-')
            ax.set_ylim([-1000, 1000])
            ax.set_xlim([0, 1])

            count = 0
            while True:
                amp_size = self.get_data_filesize()
                update_size = int(self.fs_down * self.chunk_len)

                if amp_size - plotted_samples >= update_size:
                    count = 0
                    amp_data = self.read_lowpass_data(data_fid)
                    ts = self.create_timestamp_lp(amp_data.shape[1],
                                                  start=plotted_samples)

                    amp_plot.set_data(ts, amp_data[0, :])
                    ax.set_xlim(ts[0], ts[-1])

                    fig.canvas.draw()
                    fig.canvas.flush_events()
                    plotted_samples += update_size
                else:
                    if (count + 1) % 100 == 0:
                        print('Waiting for data...')
                    if count >= 500:
                        print('Timed out. Check that the Intan '
                              'software is still recording data.')
                        break
                    time.sleep(0.01)
                    count += 1

        data_fid.close()


def get_recording_dir():
    # hide tk window
    root = tk.Tk()
    root.attributes("-alpha", 0)

    recording_dir = filedialog.askdirectory()  # get recording directory
    root.destroy()

    return recording_dir


def read_info_rhd_wrapper(recording_dir, verbose=True):
    info_path = recording_dir + '/info.rhd'
    fileinfo = read_data(info_path, verbose=verbose)
    return fileinfo


def parse_settings(recording_dir):
    settings_path = recording_dir + '/settings.xml'
    if os.path.exists(settings_path):
        return ET.parse(settings_path)
    return False


def get_downrate_from_settings(settings_etree):
    gen_config = [x for x in settings_etree.iter() if x.tag == 'GeneralConfig']
    if len(gen_config) > 0:
        gen_config = gen_config[0]
        if 'LowpassWaveformDownsampleRate' in gen_config.attrib:
            return int(gen_config.attrib['LowpassWaveformDownsampleRate'])
    return False
