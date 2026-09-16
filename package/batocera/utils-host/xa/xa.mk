################################################################################
#
# xa
#
################################################################################

XA_VERSION = 2.4.1
XA_SOURCE=xa-$(XA_VERSION).tar.gz
XA_SITE = https://www.floodgap.com/retrotech/xa/dists

define HOST_XA_BUILD_CMDS
	cd $(@D)/src && \
	for src in \
		xa.c xaa.c xal.c xap.c xat.c xar.c xar2.c \
		xao.c xau.c xam.c xacharset.c xalisting.c; \
	do \
		obj="$${src%.c}.o"; \
		$(HOSTCC_NOCCACHE) $(HOST_CFLAGS) -I. \
			-c "$$src" -o "$$obj" || exit 1; \
	done
	cd $(@D)/src && \
		$(HOSTCC_NOCCACHE) $(HOST_LDFLAGS) \
		-o ../xa \
		xa.o xaa.o xal.o xap.o xat.o xar.o xar2.o \
		xao.o xau.o xam.o xacharset.o xalisting.o
endef

define HOST_XA_INSTALL_CMDS
	$(INSTALL) -D -m 0755 $(@D)/xa $(HOST_DIR)/usr/bin/xa ;
endef

$(eval $(host-generic-package))
