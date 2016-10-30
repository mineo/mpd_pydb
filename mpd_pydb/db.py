#!/usr/bin/env python
# coding: utf-8
# Copyright © 2015 Wieland Hoffmann
# License: MIT, see LICENSE for details
"""
MPD PyDB
========
"""
from collections import namedtuple
from gzip import open
from pathlib import Path
from os.path import join
from sys import version_info

_SUPPORTED_FORMAT_VERSION = 2
_DIRECTORY_BEGIN = "begin"
_DIRECTORY_END = "end"
_FORMAT = "format"
_INFO_END = "info_end"
_MPD_VERSION = "mpd_version"
_MTIME = "mtime"
_SONG_BEGIN = "song_begin"
_SONG_END = "song_end"
_TAG = "tag"
_TIME = "Time"

_PY2 = version_info < (3,)


class Database(object):
    def __init__(self, format_version, mpd_version, supported_tags, songs=None):
        """
        :param int format_version:
        :param str mpd_version:
        :param iterable supported_tags:
        :param songs: A list of songs in the database
        :type songs: [namedtuple]
        :raises ValueError: If the format_version is not supported or
                            mpd_version is None
        :raises TypeError: If ``supported_tags`` is not iterable
        """
        if (format_version != _SUPPORTED_FORMAT_VERSION):
            raise ValueError("Format {version} is not supported".
                             format(version=format_version))

        if mpd_version is None:
            raise ValueError("mpd_version can't be None")

        #: The database format version
        self.format_version = format_version
        #: The version of MPD that created this database
        self.mpd_version = mpd_version
        #: A :class:`list` of songs in this database
        self.songs = songs or []
        #: A :class:`list` containing the names of all supported tags
        self.supported_tags = supported_tags

    def add_song(self, song):
        """
        Add ``song`` to this DB.

        :param namedtuple song:
        """
        self.songs.append(song)

    @classmethod
    def read_file(cls, filename, music_dir=None):
        """
        Read the database in ``filename``.

        :param str filename: The path to the database file
        :param str music_dir: The path to MPDs music directory
        """
        current_directory = None
        current_song = None
        current_song_tags = {}
        db = None
        format = 0
        mpd_version = None
        song_type = None
        tag_names = ["Time", "mtime", "path"]

        with open(filename, "r") as db_file:
            for line in db_file.readlines():
                split_line = line.decode("utf-8").strip().split(":", 1)

                key = split_line[0]
                if key == _INFO_END:
                    db = cls(format, mpd_version, tag_names)

                    class Song(namedtuple("Song",
                                          tag_names + ["music_dir_"])):
                        def __fspath__(self):
                            if self.music_dir_ is None:
                                raise NotImplementedError

                            return join(self.music_dir_, str(self.path))

                    song_type = Song
                elif key == _DIRECTORY_END:
                    current_directory = current_directory.parent
                elif key == _SONG_BEGIN:
                    current_song_tags = {tag: None for tag in tag_names}
                elif key == _SONG_END:
                    current_song = song_type(music_dir_=music_dir,
                                             **current_song_tags)
                    db.add_song(current_song)

                if len(split_line) == 1:
                    # info_begin or info_end
                    continue

                value = split_line[1].strip()
                if key == _TAG:
                    tag_names.append(value)
                elif key == _FORMAT:
                    format = int(value)
                elif key == _MPD_VERSION:
                    mpd_version = value
                elif key == _DIRECTORY_BEGIN:
                    current_directory = Path(value)
                elif key == _SONG_BEGIN:
                    if _PY2:
                        filename = value.encode("utf-8")
                    else:
                        filename = value
                    if current_directory is not None:
                        current_song_tags["path"] = (current_directory /
                                                     filename)
                    else:
                        # Songs in MPDs music root are not in any directory
                        current_song_tags["path"] = Path(filename)
                elif key == _TIME:
                    current_song_tags[key] = float(value)
                elif key == _MTIME:
                    current_song_tags[key] = int(value)
                elif key in tag_names:
                    current_song_tags[key] = value

        return db

    @staticmethod
    def _extract(series, index):
        def extractor(value):
            if value is None:
                return value
            if "/" not in value:
                if index == 0:
                    return value
                else:
                    return None
            return int(value.split("/", 1)[index])
        return series.apply(extractor)

    def to_dataframe(self):
        """
        Convert this database to a pandas DataFrame. In addition to the tags
        already loaded, the two columns ``TotalDiscs`` and ``TotalTracks`` will
        be populated with the values from ``Disc`` and ``Track`` tags
        (ID3 only). The ``Disc`` and ``Track`` tags will no longer contain
        information about the total amount of discs and tracks after the
        conversion.

        :rtype: :class:`~pd:pandas.DataFrame`

        """
        import pandas as pd
        df = pd.DataFrame.from_records(self.songs, columns=self.supported_tags)
        return df.assign(Track=self._extract(df["Track"], 0),
                         TotalTracks=self._extract(df["Track"], 1),
                         Disc=self._extract(df["Disc"], 0),
                         TotalDiscs=self._extract(df["Disc"], 1))
