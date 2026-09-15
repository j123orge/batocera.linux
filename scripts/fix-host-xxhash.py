from pathlib import Path
import re

p = Path("buildroot/package/xxhash/xxhash.mk")
s = p.read_text()

build_pattern = r"define HOST_XXHASH_BUILD_CMDS.*?endef"

build_replacement = """define HOST_XXHASH_BUILD_CMDS
\t$(HOST_XXHASH_ENV) $(HOSTCC_NOCCACHE) $(HOST_CFLAGS) -I$(@D) -I$(@D)/cli -c $(@D)/xxhash.c -o $(@D)/xxhash.o
\t$(HOST_XXHASH_ENV) $(HOSTCC_NOCCACHE) $(HOST_CFLAGS) -I$(@D) -I$(@D)/cli -c $(@D)/cli/xxhsum.c -o $(@D)/cli/xxhsum.o
\t$(HOST_XXHASH_ENV) $(HOSTCC_NOCCACHE) $(HOST_CFLAGS) -I$(@D) -I$(@D)/cli -c $(@D)/cli/xsum_os_specific.c -o $(@D)/cli/xsum_os_specific.o
\t$(HOST_XXHASH_ENV) $(HOSTCC_NOCCACHE) $(HOST_CFLAGS) -I$(@D) -I$(@D)/cli -c $(@D)/cli/xsum_arch.c -o $(@D)/cli/xsum_arch.o
\t$(HOST_XXHASH_ENV) $(HOSTCC_NOCCACHE) $(HOST_CFLAGS) -I$(@D) -I$(@D)/cli -c $(@D)/cli/xsum_output.c -o $(@D)/cli/xsum_output.o
\t$(HOST_XXHASH_ENV) $(HOSTCC_NOCCACHE) $(HOST_CFLAGS) -I$(@D) -I$(@D)/cli -c $(@D)/cli/xsum_sanity_check.c -o $(@D)/cli/xsum_sanity_check.o
\t$(HOST_XXHASH_ENV) $(HOSTCC_NOCCACHE) $(HOST_CFLAGS) -I$(@D) -I$(@D)/cli -c $(@D)/cli/xsum_bench.c -o $(@D)/cli/xsum_bench.o
\t$(HOST_XXHASH_ENV) $(MAKE) $(HOST_XXHASH_OPTS) DISPATCH=0 -C $(@D)
endef"""

s, n1 = re.subn(
    build_pattern,
    build_replacement,
    s,
    count=1,
    flags=re.S
)

install_pattern = r"define HOST_XXHASH_INSTALL_CMDS.*?endef"

install_replacement = """define HOST_XXHASH_INSTALL_CMDS
\t$(HOST_XXHASH_ENV) $(MAKE) $(HOST_XXHASH_OPTS) DISPATCH=0 -C $(@D) install
endef"""

s, n2 = re.subn(
    install_pattern,
    install_replacement,
    s,
    count=1,
    flags=re.S
)

print("build substituicoes:", n1)
print("install substituicoes:", n2)

if n1 != 1 or n2 != 1:
    raise SystemExit("PATCH XXHASH NAO FOI APLICADO")

p.write_text(s)
