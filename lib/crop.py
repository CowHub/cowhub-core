import cv2
import numpy as np
import sys


def read_image(image):
    return cv2.imread(image, 0)


def main(image_file, show=False):
    image = read_image(image_file)
    if show:
        cv2.imshow('original', image)

    smoothened_image = cv2.bilateralFilter(image, 5, 150, 30)  # cv2.GaussianBlur(image, (5, 5), 1.5)
    if show:
        cv2.imshow('blurred', smoothened_image)

    edges = cv2.Canny(smoothened_image, 150, 160)
    if show:
        cv2.imshow('edges', edges)

    h, w = image.shape[:2]
    _, contours0, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    contours = [cv2.approxPolyDP(cnt, 3, True) for cnt in contours0]

    # {
    vis = np.zeros((h, w, 3), np.uint8)
    cv2.drawContours(vis, contours, -1, (128, 255, 255), 2, cv2.LINE_AA)
    if show:
        cv2.imshow('contours', vis)
    # }

    if show:
        cv2.waitKey()
        cv2.destroyAllWindows()
    else:
        return smoothened_image, edges, vis

if __name__ == '__main__':
    main(sys.argv[1])
