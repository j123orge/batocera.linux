from pathlib import Path

p = Path("buildroot/package/lua/lua.mk")
lines = p.read_text().splitlines(keepends=True)

found = False

for i, line in enumerate(lines):
    if line.strip() == "define HOST_LUA_BUILD_CMDS":
        for j in range(i + 1, min(i + 8, len(lines))):
            if "$(HOST_MAKE_ENV) $(MAKE)" in lines[j]:
                if "$(MAKE) -j1" not in lines[j]:
                    lines[j] = lines[j].replace(
                        "$(MAKE)",
                        "$(MAKE) -j1",
                        1
                    )
                found = True
                break
        break

if not found:
    raise SystemExit("HOST_LUA_BUILD_CMDS nao encontrado")

p.write_text("".join(lines))

print("host-lua configurado para -j1")
