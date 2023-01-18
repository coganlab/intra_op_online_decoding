# %%
# imports
import RHX_realtime_reader as rhx_acq

rd = "F:/intan_streaming_test/data_save_testing"
realtime_reader = rhx_acq.RHX_realtime_reader(recording_dir=rd, chunk_len=0.5)


# %% Plot current data from first channel

# ts, amp_data = realtime_reader.current_acquire(plot=True)
# print(ts.shape, amp_data.shape)

# %% Plot continuously updating data

realtime_reader.realtime_acquire(plot=True)
