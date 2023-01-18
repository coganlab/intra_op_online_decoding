import pytest
import os

current = os.path.dirname(os.path.realpath(__file__))
test_data_dir = current + "/../../../test_data"


@pytest.mark.parametrize("bytes", [240640])
def test_get_timestamp_filesize(bytes):
    from RHX_realtime_reader import get_timestamp_filesize
    # from RHX_realtime_reader import (
    #     get_timestamp_filesize)
    assert get_timestamp_filesize(test_data_dir + "/time.dat") == \
        int(bytes/4)


@pytest.mark.parametrize("bytes, num_chan", [(7700480, 64)])
def test_get_data_filesize(bytes, num_chan):
    from RHX_realtime_reader import get_data_filesize
    assert get_data_filesize(test_data_dir + "/amplifier.dat",
                             num_chan) == int(bytes/(2*num_chan))


@pytest.mark.parametrize("fs, num_chan", [(30000, 64)])
def test_read_info_rhd_wrapper(fs, num_chan):
    from RHX_realtime_reader import read_info_rhd_wrapper
    fileinfo = read_info_rhd_wrapper(test_data_dir, verbose=False)
    assert fileinfo['frequency_parameters']['amplifier_sample_rate'] == fs
    assert len(fileinfo['amplifier_channels']) == num_chan


def test_read_timestamp():
    from RHX_realtime_reader import (read_timestamp, CHUNK_LENGTH,
                                     read_info_rhd_wrapper)
    finfo = read_info_rhd_wrapper(test_data_dir, verbose=False)
    fs = finfo['frequency_parameters']['amplifier_sample_rate']

    with open(test_data_dir + "/time.dat", 'rb') as ts_id:
        ts = read_timestamp(ts_id, fs)
    assert len(ts) == CHUNK_LENGTH*fs
    assert ts[0] == 0
    assert ts[1] == 1 / fs
    assert ts[-1] == (CHUNK_LENGTH*fs - 1) / fs


def test_read_amp_data():
    from RHX_realtime_reader import (read_amp_data, CHUNK_LENGTH,
                                     read_info_rhd_wrapper)
    finfo = read_info_rhd_wrapper(test_data_dir, verbose=False)
    fs = finfo['frequency_parameters']['amplifier_sample_rate']
    num_chan = len(finfo['amplifier_channels'])

    with open(test_data_dir + "/amplifier.dat", 'rb') as amp_id:
        amp_data = read_amp_data(amp_id, finfo, fs)
    assert amp_data.shape == (num_chan, CHUNK_LENGTH*fs)
