import re

with open("C:/tmp/dg_edicoes.html", "rb") as f:
    raw = f.read().decode("utf-8", errors="replace")

print(f"HTML len: {len(raw)}")

# Find JS src files
srcs = re.findall(r'src=["\']([^"\']+)["\']', raw)
custom_js = [s for s in srcs if ".js" in s and "diogrande" in s]
print(f"\nCustom JS files ({len(custom_js)}):")
for s in custom_js[:10]:
    print(" ", s)

all_js = [s for s in srcs if ".js" in s]
print(f"\nAll JS files ({len(all_js)}):")
for s in all_js[:20]:
    print(" ", s[:100])

# Find fetch/ajax/api patterns
fetches = re.findall(r"(?:fetch|XMLHttp|ajax|\.get\s*\()[^;]{0,300}", raw, re.I)
print(f"\nFetch/Ajax patterns ({len(fetches)}):")
for f in fetches[:5]:
    print(" ", f[:200])

# Find BotaoBuscar handler
idx = raw.find("BotaoBuscar")
if idx >= 0:
    print(f"\nBotaoBuscar context:")
    print(raw[max(0, idx-50):idx+500])
