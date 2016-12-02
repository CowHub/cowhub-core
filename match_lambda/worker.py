import cv2
import pickle

from descriptor import get_descriptor
from edging import get_edge

def read_blob(blob):
    sbuf = StringIO()
    sbuf.write(blob)
    pimg = Image.open(sbuf)
    return cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)

def generate_descriptor(blob):
    image = read_blob(blob)
    _, edge = get_edge(image)
    return get_descriptor(edge)

def calc_diff(source, target):
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(source, target)
    return reduce(lambda a, b: a + b.distance, matches, 0.0)

def find_match(blob, potential_matches):
    descriptor = get_descriptor(blob)
    diff = sys.maxint
    for potential_match in potential_matches:
        d = calc_diff(descriptor, pickle.load(potential_match['Value']))
        if d < diff:
            diff = d
            match = potential_match['Key']
    return match[18:]

if __name__ == "__main__":
    image = read_blob(sys.argv[1])
    descriptor = generate_descriptor(image)
    encoded_descriptor = pickle.dumps(descriptor)
    print(encoded_descriptor)
