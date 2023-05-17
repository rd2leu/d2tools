# src/db.py

import json
import jsonpickle as jp
#import dbm.dumb as ddbm
#import sqlite3
import lmdbm # LMDB with dbm-style interface

# feel free to substitue with whatever database you like
# https://github.com/Dobatymo/lmdb-python-dbm
class storage(lmdbm.Lmdb):
    _indent = 4
    def __init__(self, *args, **kwargs):
        # hacky
        if len(args) or len(kwargs):
            super().__init__(*args, **kwargs)
        else:
            for k, v in super().open('cache.db', 'c').__dict__.items():
                setattr(self, k, v)
    def _pre_key(self, value):
        return value.encode('utf-8')
    def _post_key(self, value):
        return value.decode('utf-8')
    def _pre_value(self, value):
        return jp.encode(value, indent = self._indent).encode('utf-8')
    def _post_value(self, value):
        return jp.decode(value.decode('utf-8'))

if __name__ == '__main__':
    s = storage()
    s['url'] = {'data': 1}
    print(s['url'])
