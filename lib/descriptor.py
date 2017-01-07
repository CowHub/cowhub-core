import cv2
import numpy as np

# cv2.ocl.setUseOpenCL(False)


def get_descriptor(edges, harris_threshold=100):
    harris_corners = cv2.cornerHarris(edges, 4, 3, 0.04, borderType=cv2.BORDER_DEFAULT)

    harris_normalised = np.copy(harris_corners)
    cv2.normalize(harris_corners, harris_normalised, 0, 255, cv2.NORM_MINMAX, cv2.CV_32FC1)

    key_points = []
    for (x, y), value in np.ndenumerate(harris_normalised):
        if value > harris_threshold:
            key_points.append(cv2.KeyPoint(x, y, 1))

    orb_descriptor = cv2.ORB_create()
    return orb_descriptor.compute(edges, key_points)


if __name__ == '__main__':
    import sys

    source_image = sys.argv[1]

    from datetime import datetime
    from edging import get_edge

    c1 = datetime.now()
    _, source_edge = get_edge(image_file=source_image)
    c2 = datetime.now()
    _, source = get_descriptor(source_edge)
    c3 = datetime.now()

    print "edge generation took", c2 - c1, "s"
    print "descriptor generation took", c3 - c2, "s"
