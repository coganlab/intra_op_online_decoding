# %%
# imports
import matplotlib.pyplot as plt
import numpy as np
import time

import RHX_realtime_reader as rhx_acq

rd = "F:/intan_streaming_test/data_save_testing"
realtime_reader = rhx_acq.RHX_realtime_reader(recording_dir=rd)

# %% Determine write interval

amp_timesteps = realtime_reader.get_data_filesize()

# write_len = 10000
# write_times = np.zeros(write_len)
# write_amount = np.zeros(write_len)
# write_count = 0
# start = time.time()
# while write_count < write_len:
#     temp_amp_timesteps = realtime_reader.get_data_filesize()
#     if temp_amp_timesteps > amp_timesteps:
#         write_times[write_count] = time.time() - start
#         write_amount[write_count] = temp_amp_timesteps - amp_timesteps
#         start = time.time()
#         amp_timesteps = temp_amp_timesteps
#         write_count += 1
#     else:
#         time.sleep(0.001)

# write_times = write_times[100:]
# print(f'Average time between writes: {np.mean(write_times)}')
# print(f'Median time between writes: {np.median(write_times)}')
# print(f'Max time between writes: {np.max(write_times)}')

# plt.hist(write_times, bins=15)
# plt.show()

# write_amount = write_amount[100:]
# print(f'Average amount written: {np.mean(write_amount)}')
# print(f'Median amount written: {np.median(write_amount)}')
# print(f'Max amount written: {np.max(write_amount)}')

# plt.hist(write_amount, bins=15)
# plt.show()
