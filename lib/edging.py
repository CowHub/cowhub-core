import cv2
import numpy as np

from thinning import thinning

WIDTH = 360


def get_edge(image_file, show=False):
    # Read image
    image = cv2.imread(image_file, 0)

    # Resize image
    old_height, old_width = image.shape
    new_width = WIDTH
    new_height = int((new_width * old_height) / old_width)
    resized_image = cv2.resize(image, (new_width, new_height))

    # Reduce image noise
    smoothened_image = cv2.bilateralFilter(resized_image, 5, 150, 30)

    # Normalise image
    normalised_image = cv2.normalize(smoothened_image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)

    # Get image edge
    grad_x = cv2.Sobel(normalised_image, cv2.CV_16S, 1, 0)
    grad_y = cv2.Sobel(normalised_image, cv2.CV_16S, 0, 1)
    sobel_x = cv2.convertScaleAbs(grad_x)
    sobel_y = cv2.convertScaleAbs(grad_y)
    edges = cv2.addWeighted(sobel_x, 0.5, sobel_y, 0.5, 0)

    # Convert edges to binary
    _, binary_edges = cv2.threshold(edges, cv2.mean(edges)[0], 255, cv2.THRESH_BINARY)

    # Thin binary edges
    thinned_edges = thinning(binary_edges)

    if show:
        cv2.imshow("binary edges", binary_edges)
        cv2.imshow("thinned", thinned_edges)
        cv2.waitKey()

    # Display process steps
    # cv2.imshow('original', resized_image)
    # cv2.imshow('blurred', smoothened_image)
    # cv2.imshow('normalised', normalised_image)
    # cv2.imshow('edges', edges)
    # cv2.imshow('binary', binary_edges)
    # cv2.imshow('thinned', thinned_edges)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    return smoothened_image, thinned_edges


if __name__ == '__main__':
    import sys

    get_edge(sys.argv[1], show=True)
