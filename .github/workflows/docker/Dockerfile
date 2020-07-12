################################################################
# Build stage

FROM ubuntu:20.04 AS build

ENV CBMC_SOURCE=/tmp/cbmc-source
ENV CBMC_STAGING=/tmp/cbmc-staging
ENV CBMC_INSTALL=/

ENV DESTDIR=${CBMC_STAGING}

# build dependencies
ENV DEBIAN_FRONTEND="noninteractive"
ENV TZ="America/New_York"
RUN \
  apt update && apt install -y \
    bison \
    cmake \
    flex \
    g++ \
    git \
    jq \
    libxml2-utils \
    maven \
    ninja-build \
    python-is-python3 \
    python3 \
    python3-pip \
  && rm -rf /var/lib/apt/lists/*

# build
COPY . ${CBMC_SOURCE}
RUN \
  cd ${CBMC_SOURCE} && \
  rm -rf build && \
  git submodule update --init && \
  cmake -S. -Bbuild -GNinja && \
  cd build && ninja

# # test
# RUN \
#   cd ${CBMC_SOURCE}/build && \
#   ctest -j4 -L CORE --output-on-failure

# stage
RUN cd ${CBMC_SOURCE}/build && ninja install

################################################################
# Runtime stage

FROM ubuntu:20.04

VOLUME ["/home"]

ENV CBMC_SOURCE=/tmp/cbmc-source
ENV CBMC_STAGING=/tmp/cbmc-staging
ENV CBMC_INSTALL=/

ENV PATH="/usr/local/bin:/usr/local/cbmc-viewer:${PATH}"
ENV PS1="cbmc:\w "

RUN echo PS1=\"${PS1}\" >> /root/.bashrc

# runtime dependencies
ENV DEBIAN_FRONTEND="noninteractive"
ENV TZ="America/New_York"
RUN \
  apt update && apt install -y \
    cmake \
    g++ \
    make \
    ninja-build \
    python-is-python3 \
    python3 \
    python3-pip \
  && rm -rf /var/lib/apt/lists/*

# install
COPY --from=build ${CBMC_STAGING} ${CBMC_STAGING}
RUN \
  mkdir -p ${CBMC_INSTALL} && \
  cp -RP ${CBMC_STAGING}/* ${CBMC_INSTALL}
