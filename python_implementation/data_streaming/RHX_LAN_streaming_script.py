# %% Setup
import numpy as np
import time
import matplotlib.pyplot as plt
import os

import RHX_realtime_reader as rhx_acq

rd = "F:/intan_streaming_test/data_save_testing"
ld = "F:/intan_streaming_test/LAN_testing"
realtime_reader = rhx_acq.RHX_realtime_reader(recording_dir=rd, lan_dir=ld)

# %% Get times of data acquisition and save new data to LAN directory

write_len = 500
start_times = np.zeros(write_len)
write_amount = np.zeros(write_len)
write_count = 0

data_fid = open(realtime_reader.lowpass_path, 'rb')
amp_timesteps = realtime_reader.get_data_filesize()
start = time.time()

lan_data_name = ld + '/lowpass.dat'
if os.path.exists(lan_data_name):
    os.remove(lan_data_name)

with open(lan_data_name, 'ab') as lan_fid:  # create file in LAN dir
    while write_count < write_len:
        # check if new data has been written to file
        temp_amp_timesteps = realtime_reader.get_data_filesize()
        if temp_amp_timesteps > amp_timesteps:
            # track times since start to compare to times tracked in LAN dir
            start_times[write_count] = time.time() - start

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

# np.save(ld + '/open_times.npy', start_times)

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
