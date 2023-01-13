import pytest
# add parent dir to path for imports
import sys
import os

# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))

# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
print(parent)

# adding the parent directory to
# the sys.path.
sys.path.append(parent)


@pytest.mark.parametrize("bytes", [240640])
def test_get_timestamp_filesize(bytes):
    from RHXAcquisitionFilePerSignalType import (
        get_timestamp_filesize)
    assert get_timestamp_filesize(current + "/../../test_data/time.dat") == \
        int(bytes/4)


@pytest.mark.parametrize("bytes, num_chan", [(7700480, 64)])
def test_get_data_filesize(bytes, num_chan):
    from RHXAcquisitionFilePerSignalType import (
        get_data_filesize)
    assert get_data_filesize(current + "/../../test_data/amplifier.dat",
                             num_chan) == int(bytes/(2*num_chan))


@pytest.mark.parametrize("fs, num_chan", [(30000, 64)])
def test_read_info_rhd_wrapper(fs, num_chan):
    from RHXAcquisitionFilePerSignalType import (
        read_info_rhd_wrapper)
    rd = current + "/../../test_data"
    fileinfo = read_info_rhd_wrapper(rd, verbose=False)
    assert fileinfo['frequency_parameters']['amplifier_sample_rate'] == fs
    assert len(fileinfo['amplifier_channels']) == num_chan


def test_read_timestamp():
    from RHXAcquisitionFilePerSignalType import (
        read_timestamp, CHUNK_LENGTH, read_info_rhd_wrapper)
    rd = current + "/../../test_data"
    finfo = read_info_rhd_wrapper(rd, verbose=False)
    fs = finfo['frequency_parameters']['amplifier_sample_rate']

    with open(rd + "/time.dat", 'rb') as ts_id:
        ts = read_timestamp(ts_id, fs)
    assert len(ts) == CHUNK_LENGTH*fs
    assert ts[0] == 0
    assert ts[1] == 1 / fs
    assert ts[-1] == (CHUNK_LENGTH*fs - 1) / fs


def test_read_amp_data():
    from RHXAcquisitionFilePerSignalType import (
        read_amp_data, CHUNK_LENGTH, read_info_rhd_wrapper)
    rd = current + "/../../test_data"
    finfo = read_info_rhd_wrapper(rd, verbose=False)
    fs = finfo['frequency_parameters']['amplifier_sample_rate']
    num_chan = len(finfo['amplifier_channels'])

    with open(rd + "/amplifier.dat", 'rb') as amp_id:
        amp_data = read_amp_data(amp_id, finfo, fs)
    assert amp_data.shape == (num_chan, CHUNK_LENGTH*fs)
