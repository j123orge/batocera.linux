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

new = """define HOST_ZIC_BUILD_CMDS
\t$(HOST_MAKE_ENV) $(MAKE) -j1 $(HOST_CONFIGURE_OPTS) -C $(@D) zic.o
\t$(HOST_MAKE_ENV) $(MAKE) -j1 $(HOST_CONFIGURE_OPTS) -C $(@D) zic
endef"""

p.write_text(s[:start] + new + s[end:])

print("host-zic: zic.o sera construido antes de zic")
