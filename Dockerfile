# Builder image for one EL target. The package set below is identical on
# EL8 and EL9, so the target is selected purely by the base image rather
# than by keeping a separate Dockerfile per release:
#
#   docker build --build-arg BASE_IMAGE=rockylinux:8 -t haproxy-rpm-builder:el8 .
#
# The Makefile does this for every entry in EL_VERSIONS.
ARG BASE_IMAGE=rockylinux:9
FROM ${BASE_IMAGE}

RUN dnf groupinstall -y "Development Tools" \
 && dnf install -y openssl-devel zlib-devel systemd-devel pcre-devel \
                   rpm-build redhat-rpm-config make gcc wget tar which \
 && dnf clean all

WORKDIR /build
COPY . /build

ENV USE_LUA=0 \
    USE_PROMETHEUS=0 \
    RELEASE=1

ENTRYPOINT ["/build/build.sh"]
