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

if __name__ == "__main__":
    descriptor = generate_descriptor(sys.argv[1])
    encoded_descriptor = pickle.dumps(descriptor)
    print(encoded_descriptor)
