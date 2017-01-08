import numpy as np
from sc_2739f1c0fafb0bb7062bb06fd6d958c40 import compiled_func


def _thinningIteration(im, iter):
    I, M = im, np.zeros(im.shape, np.uint8)
    compiled_func()
    return I & ~M


def thinning(src):
    dst = src.copy() / 255
    prev = np.zeros(src.shape[:2], np.uint8)
    diff = None

    while True:
        dst = _thinningIteration(dst, 0)
        dst = _thinningIteration(dst, 1)
        diff = np.absolute(dst - prev)
        prev = dst.copy()
        if np.sum(diff) == 0:
            break

    return dst * 255
