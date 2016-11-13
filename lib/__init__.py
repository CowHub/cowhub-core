import sys
import cv2
import numpy as np

from crop import main as crop


cv2.ocl.setUseOpenCL(False)


def descriptor(image, harris_threshold=100):
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


def diff(source, target):
    _, source_descriptor = descriptor(source)
    _, target_descriptor = descriptor(target)

    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(source_descriptor, target_descriptor)

    return reduce(lambda a, b: a + b.distance, matches, 0.0)


if __name__ == '__main__':
    source_image = sys.argv[1]
    target_image = sys.argv[2]

    (_, source_edge, _) = crop(image_file=source_image)
    (_, target_edge, _) = crop(image_file=target_image)

    print(diff(source_edge, target_edge))
