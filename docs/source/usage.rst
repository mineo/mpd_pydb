Usage
=====

To use this module, simply import import it::

  import mpd_pydb

and read your MPD database into an :class:`~mpd_pydb.db.Database` object::

  db = mpd_pydb.Database.read_file("/path/to/the/database.db")

Song objects
============

A song object is a :func:`~collections.namedtuple` object with each tag type
defined in the MPD database available as a field. In addition to the tag types
you can configure in MPDs configuration file, 3 additional fields are available:

Time
    The length of the song as a :class:`~float`.

mtime
    The time at which the file was last modified, in `Unix time
    <https://en.wikipedia.org/wiki/Unix_time>`_ as an :class:`~int`.

path
    The path to the file inside of MPDs music directory as an
    :class:`~pathlib:pathlib.Path` object

music_dir\_
    The absolute path to the music directory on the local hard drive. This is
    used to implement support for :pep:`519`'s :func:`os.PathLike.__fspath__`
    method on the song objects.
