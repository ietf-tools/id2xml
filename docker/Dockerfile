# This file is a docker (https://www.docker.com/what-docker) recipe, which can
# be used to build a docker image which is ready to run a datatracker in
# development mode.
#
# It is used to build an image (once you've installed docker) using a command
# like this (assuming suitable replacement of $variables):
#
# $ docker build -t ietf/datatracker:latest .
#
# To use a pre-built image, assuming we have a checked-out datatracker
# repository at /home/me/src/6.8.1.dev0, you would start (again assuming you've
# installed docker) a container from an image, as follows:
#
# $ docker run -ti -v /home/me/src/6.8.1.dev0:/root ietf/datatracker:latest

FROM ubuntu:latest
LABEL maintainer="IETF Tools Team <tools-discuss@ietf.org>"

# Default django runserver port
EXPOSE 8000

# Fetch apt package information, and upgrade to latest package versions
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -qy dist-upgrade

# Install the packages we need
RUN apt-get install -qy \
        apache2-utils \
        chromium-chromedriver \
        enscript \
        ghostscript \
        graphviz \
        libmariadbclient-dev \
        mariadb-server \
        python-is-python3 \
        python3-pip \
        yang-tools

# Get rid of installation files we don't need in the image, to reduce size
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# idnits and dependencies
ADD https://tools.ietf.org/tools/idnits/idnits /usr/local/bin/
RUN chmod +rx /usr/local/bin/idnits

# Install current datatracker dependencies
WORKDIR /root
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY docker-init.sh /docker-init.sh
RUN chmod +x /docker-init.sh
ENTRYPOINT ["/docker-init.sh"]