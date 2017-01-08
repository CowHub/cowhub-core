import cv2
import cPickle as pickle
from StringIO import StringIO
import sys
from PIL import Image
import numpy as np
import base64

from functools import reduce

from descriptor import get_descriptor
from edging import get_edge


def read_base64(data):
    data_padded = data[:].split(';')[1]
    data_padded = data_padded[6:] # Remove base64
    missing_padding = len(data_padded) % 4
    if missing_padding != 0:
        data_padded += '=' * (4 - missing_padding)

    print 'Image length (with padding):', len(data_padded)

    sbuf = StringIO()
    sbuf.write(base64.decodestring(data_padded))
    pimg = Image.open(sbuf)
    return cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2GRAY)


def generate_descriptor(image):
    _, edge = get_edge(image)
    return get_descriptor(edge)


def calc_diff(source, target):
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(source, target)
    return reduce(lambda a, b: a + b.distance, matches, 0.0)


def find_match(blob, potential_matches):
    descriptor = get_descriptor(blob)
    diff = sys.maxint
    match = None
    for potential_match in potential_matches:
        d = calc_diff(descriptor, pickle.load(potential_match['Value']))
        if d < diff:
            diff = d
            match = potential_match['Key']
    return match[18:]


if __name__ == "__main__":
    image = read_base64(open(sys.argv[1]).read())
    descriptor = generate_descriptor(image)
    encoded_descriptor = pickle.dumps(descriptor)
    print(encoded_descriptor)
