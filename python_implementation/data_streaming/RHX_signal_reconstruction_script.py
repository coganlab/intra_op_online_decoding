"""
Testing ability to read in data from RHX software, save to new directoty as a
.dat file, and then read it back in from the new directory. This will be used
to read in the lowpass data from the RHX software and save it to a directory on
a separate computer connected via ethernet. Data from the RHX software is not
saved directly to the ethernet directory due to the desire to also keep the
wideband amplifier data which is not used for realtime processing.
"""
# %% Setup
import numpy as np
import matplotlib.pyplot as plt
import shutil

import RHX_realtime_reader as rhx_acq

rd = "F:/intan_streaming_test/data_save_testing"
nd = "F:/intan_streaming_test/reconstruction_testing"
realtime_reader = rhx_acq.RHX_realtime_reader(recording_dir=rd, lan_dir=nd)

# %% Read in section of signal from recording dir
data_fid = open(realtime_reader.lowpass_path, 'rb')
read_time = 1.5  # seconds
offset_time = 0  # seconds
amp_data = realtime_reader.read_amp_data(data_fid, offset=offset_time,
                                         read_all=True)
data_fid.close()
print(amp_data.shape)

ts = np.linspace(0, amp_data.shape[1] / realtime_reader.fs_down,
                 amp_data.shape[1])
plt.figure()
plt.plot(ts, amp_data[0, :])
plt.show()

# %% Save signal to file in new directory

realtime_reader.copy_info_and_settings_to_LAN()
# info_ori = rd + "/info.rhd"
# info_new = nd + "/info.rhd"
# shutil.copy(info_ori, info_new)

# settings_new = nd + "/settings.xml"
# settings_ori = rd + "/settings.xml"
# shutil.copy(settings_ori, settings_new)

new_amp = amp_data.T / realtime_reader.MICROV_CONV
with open(nd + "/lowpass.dat", "wb") as f:
    new_amp.astype(np.int16).tofile(f)

# %% Check file sizes

new_reader = rhx_acq.RHX_realtime_reader(recording_dir=nd)
print(realtime_reader.get_data_filesize())
(new_reader.get_data_filesize())

# %% Read in signal from new directory

data_fid = open(new_reader.lowpass_path, 'rb')
read_time = 1.5  # seconds
offset_time = 1  # seconds
new_data = new_reader.read_amp_data(data_fid, offset=offset_time,
                                    read_len=read_time)
data_fid.close()
print(new_data.shape)

new_ts = np.linspace(0, new_data.shape[1] / new_reader.fs_down,
                     new_data.shape[1])
plt.figure()
plt.plot(new_ts, new_data[0, :])
plt.show()

# %%
