import sys
import cv2
import numpy as np

from crop import crop


cv2.ocl.setUseOpenCL(False)


def get_descriptor(image, harris_threshold=100):
    _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    harris_corners = cv2.cornerHarris(binary, 4, 3, 0.04, borderType=cv2.BORDER_DEFAULT)

    harris_normalised = np.copy(harris_corners)
    cv2.normalize(harris_corners, harris_normalised, 0, 255, cv2.NORM_MINMAX, cv2.CV_32FC1)

    # rescaled = cv2.convertScaleAbs(harris_normalised)
    # mixed_channels = np.zeros(rescaled.shape)
    # cv2.mixChannels([rescaled] * 3, [mixed_channels], [(0, 0), (1, 1), (2, 2)])

    key_points = []
    for (x, y), value in np.ndenumerate(harris_normalised):
        if value > harris_threshold:
            key_points.append(cv2.KeyPoint(x, y, 1))

    orb_descriptor = cv2.ORB_create()
    return orb_descriptor.compute(image, key_points)


def calc_diff(source, target):
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(source, target)

    return reduce(lambda a, b: a + b.distance, matches, 0.0)


if __name__ == '__main__':
    source_image = sys.argv[1]
    target_image = sys.argv[2]

    from datetime import datetime

    c1 = datetime.now()
    (_, source_edge, _) = crop(image_file=source_image)
    (_, target_edge, _) = crop(image_file=target_image)
    c2 = datetime.now()

    _, source = get_descriptor(source_edge)
    _, target = get_descriptor(target_edge)
    c3 = datetime.now()

    d = calc_diff(source, target)
    c4 = datetime.now()

    print c2 - c1
    print c3 - c2
    print c4 - c3
