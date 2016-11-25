import os
import pickle
import json
from redis import StrictRedis
from multiprocessing.pool import ThreadPool

HOST, PORT, PASS = tuple(os.environ[s] for s in (
    'DB_HOST',
    'DB_PORT',
    'DB_PASS',
))

MATCH = 'cattle_descriptor_*'
COUNT_EACH = 50

PREFIX_LENGTH = len('cattle_descriptor_')


class DbConn:
    def __init__(self):
        self._conn = StrictRedis(host=HOST, port=PORT, password=PASS)

    def _parse_data(self, key):
        cid = key[PREFIX_LENGTH:]
        value = self._conn.get(key)

        return cid, pickle.loads(value)

    def next_group(self, iter_id):
        cursor, data = self._conn.scan(cursor=iter_id, match=MATCH, count=COUNT_EACH)

        return cursor, ThreadPool(4).imap(self._parse_data, data)

    def write(self, cid, descriptor):
        pass

    def publish(self, cid, diff, server_id, request_id):
        self._conn.publish('match_result_%s' % (server_id, ), json.dumps({
            'request_id': request_id,
            'cattle_id': cid,
            'diff': diff
        }))
