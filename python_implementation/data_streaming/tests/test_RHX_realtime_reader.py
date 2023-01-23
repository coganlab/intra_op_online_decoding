import pytest
import os
import xml.etree.ElementTree as ET

from RHX_realtime_reader import RHX_realtime_reader

current = os.path.dirname(os.path.realpath(__file__))
test_data_dir = current + "/../../../test_data"


@pytest.mark.parametrize("fs, num_chan", [(20000, 1024)])
def test_read_info_rhd_wrapper(fs, num_chan):
    from RHX_realtime_reader import read_info_rhd_wrapper
    fileinfo = read_info_rhd_wrapper(test_data_dir, verbose=False)
    assert fileinfo['frequency_parameters']['amplifier_sample_rate'] == fs
    assert len(fileinfo['amplifier_channels']) == num_chan


@pytest.mark.parametrize("recording_dir, expected",
                         [(test_data_dir, ET.ElementTree),
                          (test_data_dir + "/info.rhd", bool)],
                         ids=['Settings present', 'No settings'])
def test_parse_settings(recording_dir, expected):
    from RHX_realtime_reader import parse_settings
    setting_info = parse_settings(recording_dir)
    assert type(setting_info) == expected
    if type(setting_info) == bool:
        assert setting_info is False


@pytest.mark.parametrize("expected",
                         [(16)])
def test_get_downrate_from_settings(expected):
    from RHX_realtime_reader import (parse_settings,
                                     get_downrate_from_settings)
    etree = parse_settings(test_data_dir)
    downrate = get_downrate_from_settings(etree)
    assert downrate == expected


def test_get_fileinfo():
    from RHX_realtime_reader import read_info_rhd_wrapper
    r = RHX_realtime_reader(recording_dir=test_data_dir, verbosity=False)
    fileinfo = read_info_rhd_wrapper(test_data_dir, verbose=False)
    assert r.fileinfo == fileinfo
    assert r.fs == fileinfo['frequency_parameters']['amplifier_sample_rate']
    assert r.num_chan == len(fileinfo['amplifier_channels'])


def test_read_settings():
    from RHX_realtime_reader import (parse_settings,
                                     get_downrate_from_settings)
    r = RHX_realtime_reader(recording_dir=test_data_dir, verbosity=False)
    downrate = get_downrate_from_settings(parse_settings(test_data_dir))
    assert r.fs_down == int(r.fs/downrate)


@pytest.mark.parametrize("bytes", [172544])
def test_get_timestamp_filesize(bytes):
    r = RHX_realtime_reader(recording_dir=test_data_dir, verbosity=False)
    assert r.get_timestamp_filesize() == int(bytes/4)


@pytest.mark.parametrize("bytes, num_chan", [(5521408, 1024)])
def test_get_data_filesize(bytes, num_chan):
    r = RHX_realtime_reader(recording_dir=test_data_dir, verbosity=False)
    assert r.get_data_filesize() == int(bytes/(2*num_chan))


def test_create_timestamp_lp():
    import numpy as np
    r = RHX_realtime_reader(recording_dir=test_data_dir, verbosity=False)
    reader_time = r.create_timestamp_lp(r.get_timestamp_filesize())
    time_arr = np.arange(0, r.get_timestamp_filesize()) / r.fs_down
    assert np.array_equal(reader_time, time_arr)


@pytest.mark.parametrize("read_all, num_chan", [(True, 1024), (False, 1024)])
def test_read_amp_data(read_all, num_chan):
    r = RHX_realtime_reader(recording_dir=test_data_dir, verbosity=False)
    amp_fid = open(test_data_dir + "/lowpass.dat", 'rb')

    amp_data = r.read_amp_data(amp_fid, read_all=read_all)

    if not read_all:
        assert amp_data.shape == (num_chan, r.chunk_len*r.fs_down)
    else:
        assert amp_data.shape == (num_chan, r.get_data_filesize())
