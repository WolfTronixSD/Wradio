"""Temporary: find HLS versions of WRadio stations and test that they play."""
import json, re, subprocess, urllib.parse
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
def get(url, t=15):
    r = subprocess.run(["curl", "-sSL", "--max-time", str(t), "-A", UA, url], capture_output=True)
    return r.stdout.decode("utf-8","replace")
names = ["1LIVE", "SWR3", "SWR1", "Bayern 3", "Bayern 1", "Deutschlandfunk", "NDR 2", "hr3", "Antenne Bayern", "Rock Antenne", "bigFM",
         "SomaFM Underground 80s", "181.fm Awesome 80s", "Nostalgie New Wave", "80s Forever"]
found = {}
for n in names:
    q = urllib.parse.quote(n)
    try: data = json.loads(get(f"https://de1.api.radio-browser.info/json/stations/byname/{q}?hidebroken=true&order=votes&reverse=true&limit=40"))
    except Exception as e: print("rb fail", n, e); data = []
    for s in data:
        for u in {s.get("url",""), s.get("url_resolved","")}:
            if ".m3u8" in u or s.get("hls") == 1:
                found.setdefault(n, set()).add((s["name"], u, s.get("codec"), s.get("bitrate")))
# ARD Audiothek: every ARD station's official livestreams
ard = get("https://api.ardaudiothek.de/organizations", 30)
want = re.compile(r"1live/|swr3|swr1|br3|bayern3|bayern1|br1|dlf|deutschlandfunk|ndr2|hr3", re.I)
for u in sorted(set(re.findall(r'https?://[^"\s]+?\.m3u8', ard))):
    if want.search(u): found.setdefault("ARD", set()).add(("ard", u, "", ""))
print("ARD bytes", len(ard))
def test(u):
    pl = get(u)
    if "#EXTM3U" not in pl: return "NOT HLS"
    lines = [l for l in pl.splitlines() if l and not l.startswith("#")]
    if "#EXT-X-STREAM-INF" in pl:
        base = u
        sub = urllib.parse.urljoin(base, lines[0])
        bw = re.findall(r"BANDWIDTH=(\d+)", pl)
        pl2 = get(sub); segs = [l for l in pl2.splitlines() if l and not l.startswith("#")]
        if not segs: return f"master ok bw={bw} but variant empty"
        seg = urllib.parse.urljoin(sub, segs[-1])
        size = len(subprocess.run(["curl","-sSL","--max-time","10","-A",UA,seg],capture_output=True).stdout)
        td = re.search(r"TARGETDURATION:(\d+)", pl2)
        return f"OK master bw={bw} target={td.group(1) if td else '?'}s seg={size}B"
    seg = urllib.parse.urljoin(u, lines[-1]) if lines else None
    size = len(subprocess.run(["curl","-sSL","--max-time","10","-A",UA,seg],capture_output=True).stdout) if seg else 0
    return f"OK media seg={size}B"
for n, items in found.items():
    print(f"\n== {n}")
    for name, u, codec, br in sorted(items)[:40]:
        print(f"  {name} | {codec} {br} | {u} -> {test(u)}")
