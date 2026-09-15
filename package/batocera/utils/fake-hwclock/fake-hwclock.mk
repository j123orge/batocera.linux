################################################################################
#
# fake-hwclock
#
################################################################################

FAKE_HWCLOCK_VERSION = 0.14
FAKE_HWCLOCK_SOURCE = fake-hwclock_$(FAKE_HWCLOCK_VERSION).tar.xz
FAKE_HWCLOCK_SITE = https://deb.debian.org/debian/pool/main/f/fake-hwclock
FAKE_HWCLOCK_LICENSE = GPL-2.0
FAKE_HWCLOCK_LICENSE_FILES = COPYING

define FAKE_HWCLOCK_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/fake-hwclock $(TARGET_DIR)/usr/sbin/fake-hwclock
	$(INSTALL) -D -m 0750 $(@D)/debian/fake-hwclock.init $(TARGET_DIR)/etc/init.d/S47fake-hwclock
	mkdir -p $(TARGET_DIR)/etc/default
	echo 'FILE=/userdata/system/fake-hwclock.data' > $(TARGET_DIR)/etc/default/fake-hwclock
	[ -f $(TARGET_DIR)/lib/lsb/init-functions ] || mkdir -p $(TARGET_DIR)/lib/lsb && echo '' > $(TARGET_DIR)/lib/lsb/init-functions
endef

$(eval $(generic-package))
