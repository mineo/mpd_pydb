#!/usr/bin/env python
# coding: utf-8
# Copyright © 2015 Wieland Hoffmann
# License: MIT, see LICENSE for details
import pytest
pytest.importorskip("pandas")

from collections import namedtuple
from mpd_pydb import db as mpd_db
from pandas import Index


@pytest.fixture
def supported_tags():
    return ["Track", "Disc"]


@pytest.fixture
def db(supported_tags):
    return mpd_db.Database(mpd_db._SUPPORTED_FORMAT_VERSION, "0.20",
                           supported_tags)


@pytest.fixture
def song_type(supported_tags):
    return namedtuple("Song", supported_tags)


def test_totaldisc_conversion(db, song_type):
    db.songs.append(song_type("1", "13/55"))
    df = db.to_dataframe()
    assert df["Disc"].values[0] == 13
    assert df["TotalDiscs"].values[0] == 55


def test_totaltrack_conversion(db, song_type):
    db.songs.append(song_type("1/2", "1"))
    df = db.to_dataframe()
    assert df["Track"].values[0] == 1
    assert df["TotalTracks"].values[0] == 2


def test_columns(db, supported_tags):
    df = db.to_dataframe()

    supported_tags.append("TotalDiscs")
    supported_tags.append("TotalTracks")
    index = Index(supported_tags)

    assert df.columns.equals(index)
