#!/bin/bash
set -euo pipefail

cd /build

# VERSION/MAINVERSION must be forwarded explicitly. The outer `make
# run-docker VERSION=x` only parameterises the docker invocation; this inner
# make is what actually selects the HAProxy tarball, and without these it
# would silently fall back to the Makefile default and build the wrong
# version. Left unset, the Makefile default still applies.
make NO_SUDO=1 \
     ${VERSION:+VERSION="$VERSION"} \
     ${MAINVERSION:+MAINVERSION="$MAINVERSION"} \
     USE_LUA="${USE_LUA:-0}" \
     USE_PROMETHEUS="${USE_PROMETHEUS:-0}" \
     RELEASE="${RELEASE:-1}"

# Hand the built packages back to the host through the /RPMS bind mount
if [ -d /RPMS ]; then
    find ./rpmbuild/RPMS ./rpmbuild/SRPMS -name '*.rpm' -exec cp -v {} /RPMS/ \;
fi
