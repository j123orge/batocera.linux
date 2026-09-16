from pathlib import Path

p = Path("buildroot/package/zic/zic.mk")
s = p.read_text()

old = """define HOST_ZIC_BUILD_CMDS
        $(HOST_MAKE_ENV) $(MAKE) $(HOST_CONFIGURE_OPTS) -C $(@D) zic
endef
"""

new = """define HOST_ZIC_BUILD_CMDS
        $(HOST_MAKE_ENV) $(MAKE) -j1 $(HOST_CONFIGURE_OPTS) -C $(@D) zic.o
        $(HOST_MAKE_ENV) $(MAKE) -j1 $(HOST_CONFIGURE_OPTS) -C $(@D) zic
endef
"""

if old not in s:
    raise SystemExit("HOST_ZIC_BUILD_CMDS esperado nao encontrado")

p.write_text(s.replace(old, new, 1))
print("host-zic: zic.o sera construido antes de zic")
