Usage
=====

To use this module, simply import import it::

  import mpd_pydb

and read your MPD database into an :class:`~mpd_pydb.db.Database` object::

  db = mpd_pydb.Database.read_file("/path/to/the/database.db")
