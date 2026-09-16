from pathlib import Path

p = Path("buildroot/package/zic/zic.mk")
s = p.read_text()

start = s.find("define HOST_ZIC_BUILD_CMDS")
if start == -1:
    raise SystemExit("HOST_ZIC_BUILD_CMDS nao encontrado")

end = s.find("endef", start)
if end == -1:
    raise SystemExit("fim de HOST_ZIC_BUILD_CMDS nao encontrado")

end += len("endef")

new = r'''define HOST_ZIC_BUILD_CMDS
	$(HOST_MAKE_ENV) $(MAKE) -j1 $(HOST_CONFIGURE_OPTS) -C $(@D) tzdir.h version.h
	cd $(@D) && \
		$(HOSTCC_NOCCACHE) $(HOST_CFLAGS) $(HOST_CPPFLAGS) \
		-c zic.c -o zic.o
	cd $(@D) && \
		$(HOSTCC_NOCCACHE) $(HOST_CFLAGS) $(HOST_LDFLAGS) \
		-o zic zic.o
endef'''

p.write_text(s[:start] + new + s[end:])

print("host-zic: headers + compilacao/link explicitos ativados")
