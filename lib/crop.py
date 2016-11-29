import cv2
import numpy as np
import sys

from thinning import thinning

WIDTH = 360


def read_image(image):
    img = cv2.imread(image, 0)
    old_height, old_width = img.shape

    new_width = WIDTH
    new_height = int((new_width * old_height) / old_width)

    return cv2.resize(img, (new_width, new_height))


def crop(image_file, show=False):
    image = read_image(image_file)
    if show:
        cv2.imshow('original', image)

    smoothened_image = cv2.bilateralFilter(image, 5, 150, 30)  # cv2.GaussianBlur(image, (5, 5), 1.5)
    if show:
        cv2.imshow('blurred', smoothened_image)

    normalised_image = cv2.normalize(smoothened_image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
    if show:
        cv2.imshow('normalised', normalised_image)

    # edges = cv2.Canny(smoothened_image, 150, 160)
    grad_x = cv2.Sobel(normalised_image, cv2.CV_16S, 1, 0)
    grad_y = cv2.Sobel(normalised_image, cv2.CV_16S, 0, 1)
    sobel_x = cv2.convertScaleAbs(grad_x)
    sobel_y = cv2.convertScaleAbs(grad_y)
    edges = cv2.addWeighted(sobel_x, 0.5, sobel_y, 0.5, 0)
    if show:
        cv2.imshow('edges', edges)

    _, binary = cv2.threshold(edges, cv2.mean(edges)[0], 255, cv2.THRESH_BINARY)
    if show:
        cv2.imshow('binary', binary)

    thinned = thinning(binary)
    if show:
        cv2.imshow('thinned', thinned)

    # {
    if False and show:
        h, w = image.shape[:2]
        _, contours0, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        contours = [cv2.approxPolyDP(cnt, 3, True) for cnt in contours0]

        vis = np.zeros((h, w, 3), np.uint8)
        cv2.drawContours(vis, contours, -1, (128, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow('contours', vis)
    # }

    if show:
        cv2.waitKey()
        cv2.destroyAllWindows()
    else:
        return smoothened_image, edges, None


if __name__ == '__main__':
    crop(sys.argv[1], show=True)
