################################################################
# Configuration

# Package version number (cbmc version number)
VERSION=5.12

# Suffix to use to distinguish a develop/HEAD build from a release
LATEST=-latest

# Debian package version to fetch debian/ folder from
DEBIAN_BASE=5.12-5

# Set GITHUB=1 to indicate that cbmc-$(VERSION) is a copy of the
# source tree (a recursive clone of the GitHub repository), and there
# is no need to download tarballs of the source code.
GITHUB=

################################################################

default: build

SRCDIR=cbmc-$(VERSION)

################################################################
# Assemble the source tree in $(SRCDIR)
#

ifeq (,$(GITHUB))
# Unless the source tree is checked out from the GitHub repository,
# assemble the source tree from tarballs.

## Download the source tree
cbmc_$(VERSION).orig.tar.gz:
ifeq (,$(LATEST))
	# For the stable release, download the tagged commit
	curl -o $@ -L \
	  https://github.com/diffblue/cbmc/archive/cbmc-$(VERSION).tar.gz
else
	# For the latest release, download latest commit on the develop branch
	curl -o $@ -L \
	  https://github.com/diffblue/cbmc/tarball/develop
endif

## Download the java models library submoduled into the cbmc repository
cbmc_$(VERSION).orig-java-models-library.tar.gz:
	curl -o $@ -L \
	  https://github.com/diffblue/java-models-library/archive/master.tar.gz

## Extract the source tree
$(SRCDIR): cbmc_$(VERSION).orig.tar.gz
	tar xzf $<
ifeq (,$(LATEST))
	mv cbmc-cbmc-$(VERSION) $@
else
	mv diffblue-cbmc-* $@
endif

## Extract the java models library.  The Debian patch files expect this
## library to be at the top level and not under src/jbmc where it is
## submoduled into the cbmc repository.
$(SRCDIR)/java-models-library: \
		$(SRCDIR) \
		cbmc_$(VERSION).orig-java-models-library.tar.gz
	cd $< && tar xzf ../cbmc_$(VERSION).orig-java-models-library.tar.gz
	mv $</java-models-library-master $</java-models-library

else
# If the source tree is checked out from the GitHub repository, we
# need to create the new source tarball for Debian and move the java
# models library to where the Debian patch files expect to find them.

cbmc_$(VERSION).orig.tar.gz:
	tar fcz $@ $(SRCDIR) \
		--exclude java-models-library  --exclude debian \
		--exclude-vcs --exclude-vcs-ignores  --exclude .github

$(SRCDIR)/java-models-library:
	mv $(SRCDIR)/jbmc/lib/java-models-library $@

endif

#
# End Assemble the source tree
################################################################

################################################################
# Assemble the debian directory
#

# We download the debian directory from the debian repository, but
# Ubuntu16 requires the use of clang due to some unicode bugs in
# libraries with the default gcc.
#
# NOTE: We should use existing artifacts instead.

DEBIAN_TARBALL=http://deb.debian.org/debian/pool/main/c/cbmc/cbmc_$(DEBIAN_BASE).debian.tar.xz
XENIAL_TARBALL=https://launchpad.net/~mt-debian/+archive/ubuntu/cbmc-backports/+sourcefiles/cbmc/5.12-5~xenial10/cbmc_5.12-5~xenial10.debian.tar.xz
UBUNTU_CODENAME=`grep UBUNTU_CODENAME /etc/os-release | cut -d= -f2`

# Download the debian directory.
$(SRCDIR)/debian: $(SRCDIR)
	if [ "$(UBUNTU_CODENAME)" = "xenial" ] ; then \
	  @ echo Downloading $(XENIAL_TARBALL); \
	  curl -L -o debian.tar.xz $(XENIAL_TARBALL); \
	  sudo apt-get -y install clang-3.8 libc++-dev libc++abi-dev; \
	else \
	  @ echo Downloading $(DEBIAN_TARBALL); \
	  curl -L -o debian.tar.xz $(DEBIAN_TARBALL); \
	fi
	cd $< && tar xJf ../debian.tar.xz
	$(RM) debian.tar.xz

# Update the debian changelog.
patch-debian-changelog: $(SRCDIR)/debian
	cd $(SRCDIR) && \
	if dpkg --compare-versions `dpkg-parsechangelog -S Version` lt $(VERSION) ; then \
		NEW_VERSION=$(VERSION)-1~auto1 ; \
	else \
	  MINOR=`dpkg-parsechangelog -S Version | cut -f2 -d- | cut -f1 -d. | cut -f1 -d~` ; \
		NEW_VERSION=$(VERSION)-`expr $$MINOR + 1`~auto1 ; \
	fi && \
	cp debian/changelog debian/changelog.orig && \
	cp changelog debian/changelog && \
	sed -i "s/#VERSION#/$$NEW_VERSION/" debian/changelog && \
	sed -i "s/#DATE#/`date -R`/" debian/changelog && \
	cat debian/changelog.orig >> debian/changelog && \
	$(RM) debian/changelog.orig

# Patch the debian control files.
# In particular, install cbmc-latest into /usr/local/cbmc-latest/bin and
# use locally-installed versions of debhelper and maven plug-in.
patch-debian-files: $(SRCDIR)/debian
ifneq (,$(LATEST))
	# Install cbmc-latest in /usr/local/cbmc-latest/bin (cbmc in /usr/bin)
	sed -i "s/^Package: cbmc.*/Package: cbmc$(LATEST)/" $(SRCDIR)/debian/control
	sed -i "s#usr/bin#usr/local/cbmc$(LATEST)/bin#" $(SRCDIR)/debian/dirs
	sed -i "s#usr/bin#usr/local/cbmc$(LATEST)/bin#" $(SRCDIR)/debian/install
	sed -i "s#usr/bin#usr/local/cbmc$(LATEST)/bin#" $(SRCDIR)/debian/links
	echo "override_dh_usrlocal:" >> $(SRCDIR)/debian/rules
	echo "\ttrue" >> $(SRCDIR)/debian/rules
	echo "override_dh_dwz:" >> $(SRCDIR)/debian/rules
	echo "\ttrue" >> $(SRCDIR)/debian/rules
	$(RM) $(SRCDIR)/debian/manpages
	sed -i "/share\/man\/man1/d" $(SRCDIR)/debian/links
endif
	# Patch debhelper version
	DEBHELPER_VERSION=`dpkg -l debhelper | tail -n1 | awk '{print $$3}' | cut -f1 -d.` ; \
	if [ $$DEBHELPER_VERSION -lt 12 ] ; then \
	  echo $$DEBHELPER_VERSION > $(SRCDIR)/debian/compat ; \
	  if [ $$DEBHELPER_VERSION -lt 10 ] ; then \
	    sed -i 's/^\tdh $$@/\tdh $$@ --parallel/' $(SRCDIR)/debian/rules ; \
	  fi ; \
	fi
	# Patch maven plug-in version
	PLUGIN_VERSION=`dpkg -l libmaven-compiler-plugin-java | tail -n1 | awk '{print $$3}' | cut -f1 -d-` ; \
	sed -i "s/^\(+[[:space:]]*<version>\).*<\/version>/\1$$PLUGIN_VERSION<\/version>/" \
	  $(SRCDIR)/debian/patches/maven*

# Patch the debian rules to build cbmc concurrently.
# See also the --parallel option added to dh above for early debhelper versions.
# This should really become part of the standard Debian build rules.
patch-debian-concurrency: $(SRCDIR)/debian
	sed -i '11s/^$$/parallel = $$(patsubst parallel=\%,\%,$$(filter parallel=\%,$$(DEB_BUILD_OPTIONS)))/' \
	  $(SRCDIR)/debian/rules
	sed -i 's/$$(MAKE)/$$(MAKE) -j$$(parallel)/' $(SRCDIR)/debian/rules

#
# End Assemble the debian directory
################################################################

patch-sources: $(SRCDIR)/debian
	sudo apt-get -y install quilt
	cd $(SRCDIR) && export QUILT_PATCHES=debian/patches && \
		while quilt push; do quilt refresh; done && quilt pop -a
	$(RM) $(SRCDIR)/debian/patches/*~

build: $(SRCDIR) $(SRCDIR)/debian $(SRCDIR)/java-models-library
	sudo apt-get -y install \
	  debhelper minisat zlib1g-dev flex bison default-jdk-headless \
	  maven maven-repo-helper maven-debian-helper \
	  libmaven-compiler-plugin-java
	$(MAKE) patch-debian-changelog
	$(MAKE) patch-debian-files
	$(MAKE) patch-debian-concurrency
	$(MAKE) patch-sources
	cd $(SRCDIR) && dpkg-buildpackage -b -Jauto -uc -d
	# upload new artifacts

clean:
	$(RM) -r $(SRCDIR)
	$(RM) cbmc_$(VERSION).orig.tar.gz
	$(RM) cbmc_$(VERSION).orig-java-models-library.tar.gz

.PHONY: default build clean
.PHONY: patch-debian-changelog patch-debian-files patch-debian-concurrency
.PHONY: patch-sources

# Copy GitHub repository to /tmp and build the package in /tmp
# Quilt won't patch special files, so using lndir in place of copy won't work.
WKDIR=/tmp/debian
REPO=`pwd`/../../..
github:
	$(RM) -r $(WKDIR)
	mkdir -p $(WKDIR)
	cp -r $(REPO) $(WKDIR)/$(SRCDIR)
	cp Makefile $(WKDIR)
	cd $(WKDIR) && make GITHUB=1
