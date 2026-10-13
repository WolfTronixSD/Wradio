"""Check that every station stream in index.html answers with audio.

Usage: python3 scripts/check_streams.py [extra URL ...]
For each URL it reports the HTTP status, content type, whether the server
allows cross-origin reads on every redirect hop (needed for the real FFT
visualizer; 'end' means only the final hop allows it, which browsers reject) and how many
bytes arrived in a few seconds. Exits 1 if a music or German station fails; ATC feeds that are offline are only listed.
"""
import re, subprocess, sys

ORIGIN = "https://wolftronixsd.github.io"
# Some servers send a "player not supported" clip to non-browser clients
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
html = open("index.html", encoding="utf-8").read()
stations = re.findall(r'\{n:\s*(\d+),\s*name:"([^"]+)",\s*url:"([^"]+)",\s*cat:"(\w+)"', html)
extra = [("+", u, u, "extra") for u in sys.argv[1:]]

def probe(url):
    out = subprocess.run(
        ["curl", "-sS", "-L", "--max-time", "6", "-H", f"Origin: {ORIGIN}", "-H", "Icy-MetaData: 0", "-A", UA,
         "-D", "-", "-o", "/dev/null", "-w", "\n__BYTES__%{size_download} __CODE__%{http_code} __URL__%{url_effective}", url],
        capture_output=True, text=True)
    text = out.stdout
    code = re.search(r"__CODE__(\d+)", text)
    size = re.search(r"__BYTES__(\d+)", text)
    final = re.search(r"__URL__(\S+)", text)
    heads = text.split("\n__BYTES__")[0].lower()
    ctype = re.findall(r"^content-type:\s*([^\r\n;]+)", heads, re.M)
    acao = re.findall(r"^access-control-allow-origin:\s*([^\r\n]+)", heads, re.M)
    # A browser needs the CORS header on every hop of a redirect chain, not just the last one
    hops = [h for h in re.split(r"\r?\n\r?\n", heads) if h.strip().startswith("http")]
    every_hop = all(re.search(r"^access-control-allow-origin:\s*(\*|" + re.escape(ORIGIN) + ")", h, re.M) for h in hops) if hops else False
    return {
        "code": code.group(1) if code else "000",
        "bytes": int(size.group(1)) if size else 0,
        "type": ctype[-1].strip() if ctype else "-",
        "cors": ("yes" if every_hop else "end") if acao and (acao[-1].strip() in ("*", ORIGIN)) else "no",
        "final": final.group(1) if final else url,
    }

bad, offline = 0, []
print(f"{'#':>3} {'name':<26} {'code':>4} {'KB':>6} {'cors':>4} type / url")
for n, name, url, cat in stations + extra:
    for u in ([url, url.replace("http://", "https://", 1)] if url.startswith("http://") else [url]):
        r = probe(u)
        # ATC feeds are low bitrate and quiet between calls, so a few KB is enough to prove they're live
        ok = r["code"].startswith("2") and "audio" in r["type"] and r["bytes"] > 2000 and "alert.mp3" not in r["final"]
        if n != "+" and u == url and not ok:
            # LiveATC feeds go offline when a volunteer's receiver is down; report, don't fail
            if cat == "atc": offline.append(name)
            else: bad += 1
        print(f"{n:>3} {name[:26]:<26} {r['code']:>4} {r['bytes']//1024:>6} {r['cors']:>4} {'OK ' if ok else 'BAD'} {r['type']} {u}"
              + (f" -> {r['final']}" if r["final"] != u else ""))
if offline:
    print("\nATC feeds offline right now (often temporary): " + ", ".join(offline))
sys.exit(1 if bad else 0)
