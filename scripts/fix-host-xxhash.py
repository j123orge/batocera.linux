from pathlib import Path
import re

p = Path("buildroot/package/xxhash/xxhash.mk")
s = p.read_text()

pattern = r"define HOST_XXHASH_BUILD_CMDS.*?endef"

replacement = """define HOST_XXHASH_BUILD_CMDS
\t$(HOST_XXHASH_ENV) $(HOSTCC_NOCCACHE) $(HOST_CFLAGS) -I$(@D) -I$(@D)/cli -c $(@D)/xxhash.c -o $(@D)/xxhash.o
\t$(HOST_XXHASH_ENV) $(HOSTCC_NOCCACHE) $(HOST_CFLAGS) -I$(@D) -I$(@D)/cli -c $(@D)/cli/xxhsum.c -o $(@D)/cli/xxhsum.o
\t$(HOST_XXHASH_ENV) $(HOSTCC_NOCCACHE) $(HOST_CFLAGS) -I$(@D) -I$(@D)/cli -c $(@D)/cli/xsum_os_specific.c -o $(@D)/cli/xsum_os_specific.o
\t$(HOST_XXHASH_ENV) $(HOSTCC_NOCCACHE) $(HOST_CFLAGS) -I$(@D) -I$(@D)/cli -c $(@D)/cli/xsum_arch.c -o $(@D)/cli/xsum_arch.o
\t$(HOST_XXHASH_ENV) $(HOSTCC_NOCCACHE) $(HOST_CFLAGS) -I$(@D) -I$(@D)/cli -c $(@D)/cli/xsum_output.c -o $(@D)/cli/xsum_output.o
\t$(HOST_XXHASH_ENV) $(HOSTCC_NOCCACHE) $(HOST_CFLAGS) -I$(@D) -I$(@D)/cli -c $(@D)/cli/xsum_sanity_check.c -o $(@D)/cli/xsum_sanity_check.o
\t$(HOST_XXHASH_ENV) $(HOSTCC_NOCCACHE) $(HOST_CFLAGS) -I$(@D) -I$(@D)/cli -c $(@D)/cli/xsum_bench.c -o $(@D)/cli/xsum_bench.o
\t$(HOST_XXHASH_ENV) $(MAKE) $(HOST_XXHASH_OPTS) DISPATCH=0 -C $(@D)
endef"""

ns, n = re.subn(pattern, replacement, s, count=1, flags=re.S)

print("substituicoes:", n)

if n != 1:
    raise SystemExit("PATCH XXHASH NAO FOI APLICADO")

p.write_text(ns)
