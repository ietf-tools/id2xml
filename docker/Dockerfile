# This file is a Docker (https://www.docker.com/why-docker) recipe, which can
# be used to run a datatracker in development mode.
#
# The "build" script in this directory can be used to build a Docker image for
# the current branch locally.
#
# To use a pre-built image, assuming we have a checked-out datatracker
# repository at /datatracker/6.8.1.dev0, you would start a container from an
# image, as follows:
#
# $ docker run -ti -v /datatracker/6.8.1.dev0:/root/src ietf/datatracker:latest

FROM ubuntu:latest
LABEL maintainer="IETF Tools Team <tools-discuss@ietf.org>"

# Default django runserver port
EXPOSE 8000

# Install all dependencies that are available as packages
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -y update && \
    apt-get -y dist-upgrade && \
    apt-get -y install -y \
        apache2-utils \
        curl \
        enscript \
        ghostscript \
        git \
        graphviz \
        libmariadbclient-dev \
        mariadb-server \
        npm \
        python-is-python3 \
        python3-pip \
        yang-tools && \
    apt-get -y clean

# Install bower
RUN npm install -g bower

# Install idnits
ADD https://tools.ietf.org/tools/idnits/idnits /usr/local/bin/
RUN chmod +rx /usr/local/bin/idnits

# Install current datatracker python dependencies
COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY docker-init.sh /docker-init.sh
RUN chmod +x /docker-init.sh

WORKDIR /root/src
ENTRYPOINT ["/docker-init.sh"]