from pathlib import Path

p = Path("buildroot/package/libtool/libtool.mk")
s = p.read_text()

old = "LIBTOOL_SITE = $(BR2_GNU_MIRROR)/libtool"
new = "LIBTOOL_SITE = https://ftp.gnu.org/gnu/libtool"

if old not in s:
    raise SystemExit("LIBTOOL_SITE esperado nao encontrado")

p.write_text(s.replace(old, new, 1))
print("libtool configurado para ftp.gnu.org")
