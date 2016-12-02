import cv2
import pickle

from descriptor import get_descriptor
from edging import get_edge

def read_blob(blob):
    sbuf = StringIO()
    sbuf.write(blob)
    pimg = Image.open(sbuf)
    return cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)

def generate_descriptor(image):
    _, edge = get_edge(image)
    return get_descriptor(edge)

if __name__ == "__main__":
    image = read_blob(sys.argv[1])
    descriptor = generate_descriptor(image)
    encoded_descriptor = pickle.dumps(descriptor)
    print(encoded_descriptor)
