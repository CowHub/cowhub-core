FROM amazonlinux:latest

WORKDIR /cowhub

RUN touch tempfile

# Setting up build env
RUN yum update -y && \
    yum install -y git cmake gcc-c++ gcc python2.7-dev chrpath wget
RUN mkdir -p /cowhub/lambda-package/cv2 /cowhub/build/numpy

# Build numpy
RUN python --version
RUN wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py
RUN pip install --prefix "/cowhub/build/numpy" numpy

RUN cp -rf /cowhub/build/numpy/lib64/python2.7/site-packages/numpy /cowhub/lambda-package

# Build OpenCV 3.1
ENV NUMPY "/cowhub/lambda-package/numpy/core/include"

WORKDIR /cowhub/build
RUN git clone https://github.com/Itseez/opencv.git

WORKDIR /cowhub/build/opencv
RUN git checkout 3.1.0
RUN mkdir /cowhub/build/opencv/build
WORKDIR /cowhub/build/opencv/build
RUN cmake										\
		-D CMAKE_BUILD_TYPE=RELEASE				\
		-D WITH_TBB=ON							\
		-D WITH_IPP=ON							\
		-D WITH_V4L=ON							\
		-D ENABLE_AVX=ON						\
		-D ENABLE_SSSE3=ON						\
		-D ENABLE_SSE41=ON						\
		-D ENABLE_SSE42=ON						\
		-D ENABLE_POPCNT=ON						\
		-D ENABLE_FAST_MATH=ON					\
		-D BUILD_EXAMPLES=OFF					\
		-D PYTHON2_NUMPY_INCLUDE_DIRS="$NUMPY"	\
		..
RUN make -j8

# RUN cp /cowhub/build/opencv/lib/cv2.so /cowhub/lambda-package/cv2/__init__.so
# RUN cp -L /cowhub/build/opencv/lib/*.so.3.1 /cowhub/lambda-package/cv2
# RUN strip --strip-all /cowhub/lambda-package/cv2/*
# RUN chrpath -r '$ORIGIN' /cowhub/lambda-package/cv2/__init__.so
# RUN touch /cowhub/lambda-package/cv2/__init__.py
#
# # Copy functions into package
# COPY lib/* lambda-package/
#
# # Zip package
# WORKDIR /cowhub/lambda-package
# RUN zip -r ../lambda-package.zip *
