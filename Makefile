HOME=$(shell pwd)
MAINVERSION?=3.4
LUA_VERSION=5.4.7
USE_LUA?=0
NO_SUDO?=1
USE_PROMETHEUS?=0
VERSION=3.4.3
ifeq ("${VERSION}","./")
	VERSION="${MAINVERSION}.0"
endif
RELEASE=1

# Supported EL targets. Override to build a subset, e.g.
#   make run-docker EL_VERSIONS=9
EL_VERSIONS?=8 9

# Base image per target. Override to use AlmaLinux, UBI, a mirror, etc:
#   make run-docker BASE_IMAGE_9=almalinux:9
BASE_IMAGE_8?=rockylinux:8
BASE_IMAGE_9?=rockylinux:9

all: build

install_prereq:
ifeq ($(NO_SUDO),1)
else
endif

clean:
ifeq ($(NO_SUDO),1)
	rm -f ./SOURCES/haproxy-${VERSION}.tar.gz
	rm -rf ./rpmbuild
	mkdir -p ./rpmbuild/SPECS/ ./rpmbuild/SOURCES/ ./rpmbuild/RPMS/ ./rpmbuild/SRPMS/
	rm -rf ./lua-${LUA_VERSION}*
else
	sudo rm -f ./SOURCES/haproxy-${VERSION}.tar.gz
	sudo rm -rf ./rpmbuild
	sudo mkdir -p ./rpmbuild/SPECS/ ./rpmbuild/SOURCES/ ./rpmbuild/RPMS/ ./rpmbuild/SRPMS/
	sudo rm -rf ./lua-${LUA_VERSION}*
endif

download-upstream:
ifeq ($(NO_SUDO),1)
	wget https://www.haproxy.org/download/${MAINVERSION}/src/haproxy-${VERSION}.tar.gz -O ./SOURCES/haproxy-${VERSION}.tar.gz
else
	sudo wget https://www.haproxy.org/download/${MAINVERSION}/src/haproxy-${VERSION}.tar.gz -O ./SOURCES/haproxy-${VERSION}.tar.gz
endif

build_lua:
ifeq ($(NO_SUDO),1)
	yum install -y readline-devel
	wget --no-check-certificate https://www.lua.org/ftp/lua-${LUA_VERSION}.tar.gz
	tar xzf lua-${LUA_VERSION}.tar.gz
	cd lua-${LUA_VERSION}
	$(MAKE) -C lua-${LUA_VERSION} clean
	$(MAKE) -C lua-${LUA_VERSION} MYCFLAGS=-fPIC linux test  # MYCFLAGS=-fPIC is required during linux ld
	$(MAKE) -C lua-${LUA_VERSION} install
else
	sudo yum install -y readline-devel
	sudo wget --no-check-certificate https://www.lua.org/ftp/lua-${LUA_VERSION}.tar.gz
	sudo tar xzf lua-${LUA_VERSION}.tar.gz
	cd lua-${LUA_VERSION}
	sudo $(MAKE) -C lua-${LUA_VERSION} clean
	sudo $(MAKE) -C lua-${LUA_VERSION} MYCFLAGS=-fPIC linux test  # MYCFLAGS=-fPIC is required during linux ld
	sudo $(MAKE) -C lua-${LUA_VERSION} install
endif

build_stages := install_prereq clean download-upstream
ifeq ($(USE_LUA),1)
	build_stages += build_lua
endif

# --- Docker builds -------------------------------------------------------
# One image and one output directory per EL target. RPMs land in
# RPMS/el8/ and RPMS/el9/ so the two builds never overwrite each other.

build-docker: $(addprefix build-docker-el,$(EL_VERSIONS))

build-docker-el%:
	docker build --build-arg BASE_IMAGE=$(BASE_IMAGE_$*) \
	             -t haproxy-rpm-builder:el$* -f Dockerfile .

run-docker: $(addprefix run-docker-el,$(EL_VERSIONS))
	@echo "==> built for EL: $(EL_VERSIONS)"
	@ls -1 RPMS/el*/*.rpm 2>/dev/null || true

run-docker-el%: build-docker-el%
	mkdir -p RPMS/el$*
	@echo "==> building for EL$* on $(BASE_IMAGE_$*)"
	docker run -e USE_LUA=${USE_LUA} -e USE_PROMETHEUS=${USE_PROMETHEUS} -e RELEASE=${RELEASE} \
	           --volume $(HOME)/RPMS/el$*:/RPMS --rm haproxy-rpm-builder:el$*

build: $(build_stages)
ifeq ($(NO_SUDO),1)
	cp -r ./SPECS/* ./rpmbuild/SPECS/ || true
	cp -r ./SOURCES/* ./rpmbuild/SOURCES/ || true
	cp ./SOURCES/examples/* ./rpmbuild/SOURCES/ || true
	rpmbuild -ba SPECS/haproxy.spec \
	--define "mainversion ${MAINVERSION}" \
	--define "version ${VERSION}" \
	--define "release ${RELEASE}" \
	--define "_topdir %(pwd)/rpmbuild" \
	--define "_builddir %{_topdir}/BUILD" \
	--define "_buildroot %{_topdir}/BUILDROOT" \
	--define "_rpmdir %{_topdir}/RPMS" \
	--define "_srcrpmdir %{_topdir}/SRPMS" \
	--define "_use_lua ${USE_LUA}" \
	--define "_use_prometheus ${USE_PROMETHEUS}"
else
	sudo cp -r ./SPECS/* ./rpmbuild/SPECS/ || true
	sudo cp -r ./SOURCES/* ./rpmbuild/SOURCES/ || true
	sudo cp ./SOURCES/examples/* ./rpmbuild/SOURCES/ || true
	sudo rpmbuild -ba SPECS/haproxy.spec \
	--define "mainversion ${MAINVERSION}" \
	--define "version ${VERSION}" \
	--define "release ${RELEASE}" \
	--define "_topdir %(pwd)/rpmbuild" \
	--define "_builddir %{_topdir}/BUILD" \
	--define "_buildroot %{_topdir}/BUILDROOT" \
	--define "_rpmdir %{_topdir}/RPMS" \
	--define "_srcrpmdir %{_topdir}/SRPMS" \
	--define "_use_lua ${USE_LUA}" \
	--define "_use_prometheus ${USE_PROMETHEUS}"
endif
