""" Script to test latency of streaming from Intan RHX software to recording
directory to LAN directory. Similar to RHX_streaming_latency_script.py, but
instead of recording delay between change in file size and time of access, for
the recording directory, this script is meant to assist in recording the delay
between change in file size in the recording directory and time of access in
the LAN directory.
    To do this, the script waits for changes to the file size of
lowpass.dat in the recording directory and then records the time of this update
to the file by the Intan RHX software. The script then reads this new data from
the lowpass.dat file and saves that chunk of data to 'lowpass.dat' in the
specified LAN directory (does not necessarily need to be a LAN-connected
directory, but that is the purpose of this script). Over the specified number
of iterations, the times of file updates by the RHX software in the recording
directory are added to a numpy array and saved as a .npy file in the LAN
directory (times are saved as timestamps from datetime.now() for a built-in
reference point that can be used to compare times on the LAN computer).
    Another script, RHX_LAN_collection_script.py, should be running at the same
time as this script on another computer to determine at what times the data is
accessible in the LAN directory. After all iterations are complete, the times
of accessiblility can be paired with the write times from this script (saved
as .npy file in the LAN directory) to determine the latency of streaming
lowpass data from the RHX software to the LAN directory.
"""
# %% Setup
import numpy as np
import time
import matplotlib.pyplot as plt
import os
from datetime import datetime

import RHX_realtime_reader as rhx_acq

rd = "F:/intan_streaming_test/data_save_testing"
ld = "F:/intan_streaming_test/LAN_testing"
realtime_reader = rhx_acq.RHX_realtime_reader(recording_dir=rd, lan_dir=ld)

# %% Get times of data acquisition and save new data to LAN directory

write_len = 10000
start_times = np.zeros(write_len)
write_amount = np.zeros(write_len)
write_count = 0

data_fid = open(realtime_reader.lowpass_path, 'rb')
amp_timesteps = realtime_reader.get_data_filesize()

lan_data_name = ld + '/lowpass.dat'
if os.path.exists(lan_data_name):
    os.remove(lan_data_name)

with open(lan_data_name, 'ab') as lan_fid:  # create file in LAN dir
    while write_count < write_len:
        # check if new data has been written to file
        temp_amp_timesteps = realtime_reader.get_data_filesize()
        if temp_amp_timesteps > amp_timesteps:
            # track times since start to compare to times tracked in LAN dir
            start_times[write_count] = datetime.timestamp(datetime.now())

            write_amount[write_count] = temp_amp_timesteps - amp_timesteps

            if write_count < 1:
                # account for time difference between start of recording and
                # access by script
                offset_time = amp_timesteps / realtime_reader.fs_down

                # read to end of file from calculated offset
                amp_data = realtime_reader.read_amp_data(data_fid,
                                                         offset=offset_time,
                                                         read_all=True)
            else:
                # read to end of file (offset not necessary because only new
                # data is being read since this is working with the same
                # file that has already been read)
                amp_data = realtime_reader.read_amp_data(data_fid,
                                                         read_all=True)
            save_data = amp_data.T / realtime_reader.MICROV_CONV
            save_data.astype(np.int16).tofile(lan_fid)

            amp_timesteps = temp_amp_timesteps
            write_count += 1
        else:
            time.sleep(0.001)

data_fid.close()
realtime_reader.copy_info_and_settings_to_LAN()

# %% Save array of open times to file

np.save(ld + '/open_times.npy', start_times)
np.save(ld + '/write_amounts.npy', write_amount)
# %%

write_times = np.diff(start_times[100:])
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


# %% Test that script saves LAN data correctly

ts_rd, amp_data_rd = realtime_reader.acquire_current(plot=False)

lan_reader = rhx_acq.RHX_realtime_reader(recording_dir=ld)
ts_lan, amp_data_lan = lan_reader.acquire_current(plot=False)

display_time = 10  # seconds
display_samp = int(display_time * lan_reader.fs_down)

plt.figure()
plt.plot(ts_rd[:display_samp], amp_data_rd[0, :display_samp])
plt.plot(ts_lan[:display_samp - int(offset_time*lan_reader.fs_down)] +
         offset_time,
         amp_data_lan[0, :display_samp - int(offset_time*lan_reader.fs_down)])
plt.ylabel('Voltage (uV)')
plt.xlabel('Time (s)')
plt.show()

# %%
