################################################################
# Configuration

# Package version number (cbmc version number)
VERSION=5.12

# Suffix to use to distinguish a develop/HEAD build from a release
LATEST=-latest

# Debian package version to fetch debian/ folder from
DEBIAN_BASE=5.12-5

# Source directory.
#
# Assemble the source directory by downloading and unpacking the
# appropriate tarballs to this directory.
#
# Set the source directory to '.' to indicate that the current
# directory is the git repository (including submodules) and
# downloading tarballs is not necessary.
SRC?=cbmc-$(VERSION)

################################################################

default: build

# Begin source tree download unless cwd is the cloned repository.
ifneq (.,$(SRC))

cbmc_$(VERSION).orig-java-models-library.tar.gz:
	curl -L -o $@ https://github.com/diffblue/java-models-library/archive/master.tar.gz

cbmc_$(VERSION).orig.tar.gz:
ifeq (,$(LATEST))
	curl -o $@ https://github.com/diffblue/cbmc/archive/cbmc-$(VERSION).tar.gz
else
	curl -o $@ -L https://github.com/diffblue/cbmc/tarball/develop
endif

$(SRC): cbmc_$(VERSION).orig.tar.gz
	tar xzf $<
ifeq (,$(LATEST))
	mv cbmc-cbmc-$(VERSION) $@
else
	mv diffblue-cbmc-* $@
endif

$(SRC)/java-models-library: $(SRC) cbmc_$(VERSION).orig-java-models-library.tar.gz
	cd $< && tar xzf ../cbmc_$(VERSION).orig-java-models-library.tar.gz
	mv $</java-models-library-master $</java-models-library

endif
# End source tree download

$(SRC)/debian: $(SRC)
	# should get existing artifacts instead
	curl -o /tmp/debian.tar.xz http://deb.debian.org/debian/pool/main/c/cbmc/cbmc_$(DEBIAN_BASE).debian.tar.xz
	cd $< && tar xJf /tmp/debian.tar.xz
	$(RM) /tmp/debian.tar.xz

$(SRC)/debian/compat: $(SRC)/debian
	# fakeroot debian/rules clean complains about a missing debian/compat
	# debian/control gives debhelper-compat = 13
	# debian/compat maximum value accepted is 10 on Ubuntu16
	# confirm this will not overwrite a preexisting debian/compat
	echo "10" > $@

$(SRC)/debian/changelog: $(SRC)/debian
	cd $(SRC) && \
	if dpkg --compare-versions `dpkg-parsechangelog -S Version` lt $(VERSION) ; then \
		NEW_VERSION=$(VERSION)-1~auto1 ; \
	else \
	  MINOR=`dpkg-parsechangelog -S Version | cut -f2 -d- | cut -f1 -d.` ; \
		NEW_VERSION=$(VERSION)-`expr $$MINOR + 1`~auto1 ; \
	fi ; \
	cp debian/changelog debian/changelog.orig ; \
	cd .. ; \
	cp changelog $@ ; \
	sed -i "s/#VERSION#/$$NEW_VERSION/" $@
	sed -i "s/#DATE#/`date -R`/" $@
	cat $(SRC)/debian/changelog.orig >> $@
	$(RM) $(SRC)/debian/changelog.orig

# Require java model library download unless cwd is the cloned repository
ifneq (.,$(SRC))
build: $(SRC)/java-models-library
endif

build: $(SRC)/debian/compat $(SRC)/debian/changelog
	sudo apt-get -y install quilt
	cd $(SRC) && export QUILT_PATCHES=debian/patches && \
		while quilt push; do quilt refresh; done && quilt pop -a
	$(RM) $(SRC)/debian/patches/*~
	sudo apt-get -y install \
		debhelper minisat zlib1g-dev flex bison default-jdk-headless \
		maven maven-repo-helper maven-debian-helper libmaven-compiler-plugin-java
ifneq (,$(LATEST))
	sed -i "s/^Package: cbmc.*/Package: cbmc$(LATEST)/" $(SRC)/debian/control
	sed -i "s#usr/bin#usr/local/cbmc$(LATEST)/bin#" $(SRC)/debian/dirs
	sed -i "s#usr/bin#usr/local/cbmc$(LATEST)/bin#" $(SRC)/debian/install
	sed -i "s#usr/bin#usr/local/cbmc$(LATEST)/bin#" $(SRC)/debian/links
	echo "override_dh_usrlocal:" >> $(SRC)/debian/rules
	echo "\ttrue" >> $(SRC)/debian/rules
	echo "override_dh_dwz:" >> $(SRC)/debian/rules
	echo "\ttrue" >> $(SRC)/debian/rules
	$(RM) $(SRC)/debian/manpages
	sed -i "/share\/man\/man1/d" $(SRC)/debian/links
endif
	PLUGIN_VERSION=`dpkg -l libmaven-compiler-plugin-java | tail -n1 | awk '{print $$3}' | cut -f1 -d-` ; \
		sed -i "s/^\(+[[:space:]]*<version>\).*<\/version>/\1$$PLUGIN_VERSION<\/version>/" \
		$(SRC)/debian/patches/maven*
	cd $(SRC) && dpkg-buildpackage -b -jauto -uc -d
	# upload new artifacts

clean:
ifneq (.,$(SRC))
	$(RM) -r $(SRC)
endif
	$(RM) cbmc_$(VERSION).orig.tar.gz
	$(RM) cbmc_$(VERSION).orig-java-models-library.tar.gz

.PHONY: build clean default
