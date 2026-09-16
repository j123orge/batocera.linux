from pathlib import Path

p = Path("buildroot/package/lua/lua.mk")
s = p.read_text()

start = s.index("define HOST_LUA_BUILD_CMDS")
end = s.index("endef", start) + len("endef")

new = r'''define HOST_LUA_BUILD_CMDS
	cd $(@D)/src && \
	for src in \
		lapi.c lcode.c lctype.c ldebug.c ldo.c ldump.c \
		lfunc.c lgc.c llex.c lmem.c lobject.c lopcodes.c \
		lparser.c lstate.c lstring.c ltable.c ltm.c lundump.c \
		lvm.c lzio.c lauxlib.c lbaselib.c lcorolib.c ldblib.c \
		liolib.c lmathlib.c loadlib.c loslib.c lstrlib.c \
		ltablib.c lutf8lib.c linit.c lua.c luac.c; \
	do \
		obj="$${src%.c}.o"; \
		$(HOSTCC_NOCCACHE) $(HOST_LUA_CFLAGS) -std=gnu99 \
			-c "$$src" -o "$$obj" || exit 1; \
	done
	$(HOST_MAKE_ENV) $(MAKE) -j1 \
		CFLAGS="$(HOST_LUA_CFLAGS)" \
		MYLDFLAGS="$(HOST_LDFLAGS)" \
		MYLIBS="$(HOST_LUA_MYLIBS)" \
		BUILDMODE=dynamic \
		PKG_VERSION=$(LUA_VERSION) -C $(@D)/src all
	sed -e "s/@VERSION@/$(LUA_VERSION)/;s/@ABI@/$(LUAINTERPRETER_ABIVER)/;s/@MYLIBS@/$(HOST_LUA_MYLIBS)/" \
		package/lua/lua.pc.in > $(@D)/lua.pc
endef'''

p.write_text(s[:start] + new + s[end:] + "\n")

print("host-lua: compilacao explicita dos objetos ativada")
