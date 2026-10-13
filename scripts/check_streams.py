"""Check that every station stream in index.html answers with audio.

Usage: python3 scripts/check_streams.py [extra URL ...]
For each URL it reports the HTTP status, content type, whether the server
allows cross-origin reads (needed for the real FFT visualizer) and how many
bytes arrived in a few seconds. Exits 1 if a station in index.html fails.
"""
import re, subprocess, sys

ORIGIN = "https://wolftronixsd.github.io"
html = open("index.html", encoding="utf-8").read()
stations = re.findall(r'\{n:\s*(\d+),\s*name:"([^"]+)",\s*url:"([^"]+)"', html)
extra = [("+", u, u) for u in sys.argv[1:]]

def probe(url):
    out = subprocess.run(
        ["curl", "-sS", "-L", "--max-time", "6", "-H", f"Origin: {ORIGIN}", "-H", "Icy-MetaData: 0",
         "-D", "-", "-o", "/dev/null", "-w", "\n__BYTES__%{size_download} __CODE__%{http_code} __URL__%{url_effective}", url],
        capture_output=True, text=True)
    text = out.stdout
    code = re.search(r"__CODE__(\d+)", text)
    size = re.search(r"__BYTES__(\d+)", text)
    final = re.search(r"__URL__(\S+)", text)
    heads = text.split("\n__BYTES__")[0].lower()
    ctype = re.findall(r"^content-type:\s*([^\r\n;]+)", heads, re.M)
    acao = re.findall(r"^access-control-allow-origin:\s*([^\r\n]+)", heads, re.M)
    return {
        "code": code.group(1) if code else "000",
        "bytes": int(size.group(1)) if size else 0,
        "type": ctype[-1].strip() if ctype else "-",
        "cors": "yes" if acao and (acao[-1].strip() in ("*", ORIGIN)) else "no",
        "final": final.group(1) if final else url,
    }

bad = 0
print(f"{'#':>3} {'name':<26} {'code':>4} {'KB':>6} {'cors':>4} type / url")
for n, name, url in [(n, name, url) for n, name, url in stations] + extra:
    for u in ([url, url.replace("http://", "https://", 1)] if url.startswith("http://") else [url]):
        r = probe(u)
        ok = r["code"].startswith("2") and r["bytes"] > 8000
        if n != "+" and u == url and not ok:
            bad += 1
        print(f"{n:>3} {name[:26]:<26} {r['code']:>4} {r['bytes']//1024:>6} {r['cors']:>4} {'OK ' if ok else 'BAD'} {r['type']} {u}"
              + (f" -> {r['final']}" if r["final"] != u else ""))
sys.exit(1 if bad else 0)
