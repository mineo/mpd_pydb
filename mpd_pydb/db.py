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


_SUPPORTED_FORMAT_VERSION = 2


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
        #: A :class:`frozenset` containing the names of all supported tags
        self.supported_tags = frozenset(supported_tags)

    def add_song(self, song):
        """
        Add ``song`` to this DB.

        :param namedtuple song:
        """
        self.songs.append(song)

    @classmethod
    def read_file(cls, filename):
        """
        Read the database in ``filename``.

        :param str filename: The path to the database file
        """
        current_song = None
        current_song_tags = {}
        db = None
        format = 0
        mpd_version = None
        song_type = None
        tag_names = ["Time", "mtime"]

        with open(filename, "r") as db_file:
            for line in db_file.readlines():
                split_line = line.decode("utf-8").strip().split(":", 1)

                key = split_line[0]
                if key == "info_end":
                    db = cls(format, mpd_version, tag_names)
                    song_type = namedtuple("Song", tag_names)
                elif key == "song_begin":
                    current_song_tags = {tag: None for tag in tag_names}
                elif key == "song_end":
                    current_song = song_type(**current_song_tags)
                    db.add_song(current_song)

                if len(split_line) == 1:
                    # info_begin or info_end
                    continue

                value = split_line[1].strip()
                if key == "tag":
                    tag_names.append(value)
                elif key == "format":
                    format = int(value)
                elif key == "mpd_version":
                    mpd_version = value
                elif key in tag_names:
                    current_song_tags[key] = value

        return db

    def to_dataframe(self):
        """
        Convert this database to a pandas DataFrame.

        :rtype: :class:`~pd:pandas.DataFrame`
        """
        import pandas as pd
        return pd.DataFrame(self.songs, columns=self.supported_tags)
