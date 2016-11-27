from PIL import Image
from StringIO import StringIO
import base64
import cv2
import numpy as np
from multiprocessing import Process, Queue, cpu_count
from Queue import Empty as QueueEmpty
import sys

from diff import calc_diff, get_descriptor
from crop import crop
from db import DbConn
from util import foreach


def read_base64(b64_string):
    sbuf = StringIO()
    sbuf.write(base64.b64decode(b64_string))
    pimg = Image.open(sbuf)
    return cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)


def base64_to_descriptor(b64_string):
    image = read_base64(b64_string)
    (_, edge, _) = crop(image)
    return get_descriptor(edge)


def start_worker(source_descriptor, redis_conn, iter_queue, res_queue):
    while True:
        iter_id = iter_queue.get()

        if iter_id < 0:
            iter_queue.put(-1)
            break

        new_cursor, rows = redis_conn.next_group(iter_id)
        new_cursor = int(new_cursor)
        iter_queue.put(new_cursor if new_cursor > 0 else -1)

        for (cid, target_descriptor) in rows:
            diff = calc_diff(source_descriptor, target_descriptor)

            (other_cid, other_diff) = res_queue.get()
            res_queue.put((cid, diff) if diff < other_diff else (other_cid, other_diff))


class Worker:
    def __init__(self):
        self._db_conn = DbConn()

    def start_processing(self, image, cid):
        descriptor = base64_to_descriptor(image)

        self._db_conn.write(cid, descriptor)

    def start_matching(self, image, server_id, request_id):
        descriptor = base64_to_descriptor(image)

        db_conn = self._db_conn
        processes = cpu_count()
        iter_queue = Queue(1)
        res_queue = Queue(1)

        res_queue.put((-1, sys.maxint))
        workers = [Process(target=start_worker, args=(descriptor, db_conn, iter_queue, res_queue))
                   for _ in range(processes)]
        foreach(lambda x: x.start(), workers)
        foreach(lambda x: x.join(), workers)

        try:
            (cid, diff) = res_queue.get(block=False)
            if cid < 0:
                raise QueueEmpty()
            db_conn.publish(cid, diff, server_id, request_id)
        except QueueEmpty:
            raise RuntimeError('No element in the result queue.')
