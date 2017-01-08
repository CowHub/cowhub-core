import cPickle as pickle
import numpy
import cv2


def kp_dumps(descriptor):
    kps, mt = descriptor
    index = numpy.empty(len(kps), dtype=tuple)
    for (i, kp) in enumerate(kps):
        index[i] = (kp.pt, kp.size, kp.angle, kp.response, kp.octave, kp.class_id)
    return pickle.dumps((index, mt))


def kp_loads(string):
    (index, mt) = pickle.loads(string)
    array = numpy.empty(index.shape, dtype=object)
    for i in range(0, index.shape):
        t = index[i]
        array[i] = cv2.KeyPoint(t[0][0], t[0][1], _size=t[1], _angle=t[2], _response=t[3], _octave=t[4], _class_id=t[5])
    return array.tolist(), mt
