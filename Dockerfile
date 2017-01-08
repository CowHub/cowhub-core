FROM amazonlinux:latest

# Install the SciPy stack on Amazon Linux and prepare it for AWS Lambda
RUN yum -y update
RUN yum -y groupinstall "Development Tools"
RUN yum -y install epel-release
RUN yum -y install blas
RUN yum -y install lapack
RUN yum -y install atlas-sse3-devel
RUN yum -y install Cython
RUN yum -y install python27
RUN yum -y install python27-numpy.x86_64
RUN yum -y install python27-numpy-f2py.x86_64
RUN yum -y install python27-scipy.x86_64
# RUN yum -y install cmake wget

# WORKDIR /
# RUN wget https://github.com/Itseez/opencv/archive/3.1.0.zip -O /opencv3.zip && \
#     unzip -q opencv3.zip && mv /opencv-3.1.0 /opencv
# RUN wget https://github.com/Itseez/opencv_contrib/archive/3.1.0.zip -O /opencv_contrib3.zip && \
#     unzip -q /opencv_contrib3.zip && mv /opencv_contrib-3.1.0 /opencv_contrib

# WORKDIR /opencv/build
# RUN cmake -D CMAKE_BUILD_TYPE=RELEASE \
# 	-D BUILD_PYTHON_SUPPORT=ON \
# 	-D CMAKE_INSTALL_PREFIX=/usr/local \
# 	-D OPENCV_EXTRA_MODULES_PATH=/opencv_contrib/modules \
# 	-D BUILD_NEW_PYTHON_SUPPORT=ON \
# 	-D WITH_IPP=OFF \
# 	-D WITH_V4L=ON ..
# RUN make -j16

WORKDIR /home/ec2-user/
RUN easy_install pip
RUN /usr/local/bin/pip install --upgrade pip
RUN mkdir -p /home/ec2-user/stack

COPY requirements.txt ./
RUN /usr/local/bin/pip install -r requirements.txt -t stack

RUN cp -R /usr/lib64/python2.7/dist-packages/numpy stack/numpy
RUN cp -R /usr/lib64/python2.7/dist-packages/scipy stack/scipy

WORKDIR /home/ec2-user/stack
RUN tar -czvf /stack.tgz *
