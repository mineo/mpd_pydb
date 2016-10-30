#!/usr/bin/env python
# coding: utf-8
# Copyright © 2015, 2016 Wieland Hoffmann
# License: MIT, see LICENSE for details
import mpd_pydb
import pytest


from io import BytesIO
from os.path import join
from pathlib import Path

try:
    from os import fspath
except Exception:
    def fspath(obj):
        _type = type(obj)
        path = _type.__fspath__(obj)
        return path


@pytest.fixture
def db():
    return mpd_pydb.Database.read_file("test/mpd.db.gz")


@pytest.fixture
def db_with_music_dir():
    return mpd_pydb.Database.read_file("test/mpd.db.gz",
                                       music_dir="/home/test/Musik")


def test_db_format(db):
    assert db.format_version == mpd_pydb.db._SUPPORTED_FORMAT_VERSION


def test_mpd_version(db):
    assert db.mpd_version == "0.20"


def test_number_of_songs(db):
    assert len(db.songs) == 12


def test_supported_tags(db):
    expected = ["Time",
                "mtime",
                "path",
                "Artist",
                "Album",
                "AlbumArtist",
                "Title",
                "Track",
                "Name",
                "Genre",
                "Date",
                "Composer",
                "Performer",
                "Disc",
                "MUSICBRAINZ_ARTISTID",
                "MUSICBRAINZ_ALBUMID",
                "MUSICBRAINZ_ALBUMARTISTID",
                "MUSICBRAINZ_TRACKID",
                "MUSICBRAINZ_RELEASETRACKID"]

    assert db.supported_tags == expected


def test_songs_have_all_supported_tags(db):
    for song in db.songs:
        for tagname in db.supported_tags:
            assert hasattr(song, tagname)


def test_tag_values(db):
    song = db.songs[0]
    expected = {"Time": 23.458000,
                "Title": "Intro",
                "MUSICBRAINZ_ALBUMARTISTID":
                "fc85edee-2156-4b4a-a4b5-6a0bf2882a7b",
                "Date": "2011-08-20",
                "Disc": "1",
                "Artist": "_ensnare_",
                "MUSICBRAINZ_ALBUMID": "14a6defe-bb0d-4394-8472-03c1c570ba98",
                "AlbumArtist": "_ensnare_",
                "MUSICBRAINZ_RELEASETRACKID":
                "7eda850d-d223-3833-b2ca-fcaf18a1a74d",
                "Album": "Impeccable Micro",
                "MUSICBRAINZ_ARTISTID": "fc85edee-2156-4b4a-a4b5-6a0bf2882a7b",
                "MUSICBRAINZ_TRACKID": "e31e6049-8b14-4789-a2e5-7933acc9bcf2",
                "Track": "1",
                "mtime": 1432207804,
                "path": Path("_ensnare_") /
                "2011 - Impeccable Micro" / "01 - Intro.flac"}

    for tag, value in expected.items():
        assert getattr(song, tag) == value


def gzip_read_mock(format):
    data = """info_begin
    format: {format}
    mpd_version: 0.20
    info_end
    """.format(format=format)
    bdata = data.encode()

    def f(*args, **kwargs):
        return BytesIO(bdata)

    return f


@pytest.mark.parametrize("format",
                         list(range(0, 10)))
def test_format_check(format, monkeypatch):
    if format == mpd_pydb.db._SUPPORTED_FORMAT_VERSION:
        pytest.skip()

    monkeypatch.setattr(mpd_pydb.db, "open", gzip_read_mock(format))
    with pytest.raises(ValueError):
        mpd_pydb.Database.read_file("")


def test_mpd_version_check(monkeypatch):
    with pytest.raises(ValueError):
        mpd_pydb.Database(mpd_pydb.db._SUPPORTED_FORMAT_VERSION,
                          None, supported_tags=[])


def test_path_nested(db):
    expected = Path("Anamanaguchi") / "Pop It.mp3"
    assert db.songs[-1].path == expected


def test_path_non_ascii(db):
    path = db.songs[8].path
    assert path == (Path("_ensnare_") /
                    "2011 - Impeccable Micro" /
                    "09 - Gavin’s Magical Rainbow Catastrophe.flac")


def test_fspath_without_music_dir(db):
    with pytest.raises(NotImplementedError):
        song = db.songs[0]
        _type = type(song)
        _type.__fspath__(song)


def test_fspath_with_music_dir(db_with_music_dir):
    song = db_with_music_dir.songs[0]
    path = fspath(song)
    assert path == join("/home", "test", "Musik", "_ensnare_",
                        "2011 - Impeccable Micro", "01 - Intro.flac")
