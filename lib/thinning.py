"""
===========================
@Author  : Linbo<linbo.me>
@Version: 1.0    25/10/2014
This is the implementation of the
Zhang-Suen Thinning Algorithm for skeletonization.
===========================
"""


def neighbours(x, y, image):
    """Return 8-neighbours of image point P1(x,y), in a clockwise order"""
    img = image
    x_1, y_1, x1, y1 = x - 1, y - 1, x + 1, y + 1
    return [img[x_1][y], img[x_1][y1], img[x][y1], img[x1][y1],  # P2,P3,P4,P5
            img[x1][y], img[x1][y_1], img[x][y_1], img[x_1][y_1]]  # P6,P7,P8,P9


def transitions(neighbours):
    """No. of 0,1 patterns (transitions from 0 to 1) in the ordered sequence"""
    n = neighbours + neighbours[0:1]  # P2, P3, ... , P8, P9, P2
    return sum((n1, n2) == (0, 255) for n1, n2 in zip(n, n[1:]))  # (P2,P3), (P3,P4), ... , (P8,P9), (P9,P2)


def thinning(image):
    """the Zhang-Suen Thinning Algorithm"""
    image_thinned = image.copy()  # deepcopy to protect the original image
    changing1 = changing2 = 1  # the points to be removed (set as 0)
    while changing1 or changing2:  # iterates until no further changes occur in the image
        # Step 1
        changing1 = []
        rows, columns = image_thinned.shape  # x for rows, y for columns
        for x in range(1, rows - 1):  # No. of  rows
            for y in range(1, columns - 1):  # No. of columns
                P2, P3, P4, P5, P6, P7, P8, P9 = n = neighbours(x, y, image_thinned)
                if (image_thinned[x][y] == 255 and
                    510 <= sum(n) <= 1530 and  # Condition 1: 2<= N(P1) <= 6
                    transitions(n) == 1 and  # Condition 2: S(P1)=1
                    any(p == 0 for p in (P2, P4, P6)) and  # Condition 3
                    any(p == 0 for p in (P4, P6, P8))):  # Condition 4
                    changing1.append((x, y))
        for x, y in changing1:
            image_thinned[x][y] = 0
        # Step 2
        changing2 = []
        for x in range(1, rows - 1):
            for y in range(1, columns - 1):
                P2, P3, P4, P5, P6, P7, P8, P9 = n = neighbours(x, y, image_thinned)
                if (image_thinned[x][y] == 255 and  # Condition 0
                    510 <= sum(n) <= 1530 and  # Condition 1
                    transitions(n) == 1 and  # Condition 2
                    any(p == 0 for p in (P2, P4, P8))and  # Condition 3
                    any(p == 0 for p in (P2, P6, P8))):  # Condition 4
                    changing2.append((x, y))
        for x, y in changing2:
            image_thinned[x][y] = 0
    return image_thinned
