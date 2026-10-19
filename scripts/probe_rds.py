"""Probe each WRadio station for song info a browser on wolftronixsd.github.io can read."""
import re, subprocess, json, urllib.parse
ORIGIN = "https://wolftronixsd.github.io"
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
html = open("index.html", encoding="utf-8").read()
st = re.findall(r'\{n:\s*(\d+),\s*name:"([^"]+)",\s*url:"([^"]+)",\s*cat:"(\w+)"', html)
def sh(args, t=8):
    try: return subprocess.run(args, capture_output=True, timeout=t+2).stdout
    except Exception as e: return b""
def heads(raw):
    blocks = re.split(rb"\r?\n\r?\n", raw)
    return blocks
for n, name, url, cat in st:
    if cat == "atc": continue
    r = {"n": n, "name": name}
    # preflight
    pf = sh(["curl","-sS","-L","-X","OPTIONS","--max-time","6","-A",UA,"-H",f"Origin: {ORIGIN}","-H","Access-Control-Request-Method: GET","-H","Access-Control-Request-Headers: icy-metadata","-D","-","-o","/dev/null",url]).decode("latin1").lower()
    ah = re.findall(r"^access-control-allow-headers:\s*([^\r\n]+)", pf, re.M)
    r["preflight_allow_headers"] = ah[-1] if ah else None
    r["preflight_status"] = (re.findall(r"^http/\S+ (\d+)", pf, re.M) or ["-"])[-1]
    # real GET with icy
    raw = sh(["curl","-sS","-L","--max-time","8","-A",UA,"-H",f"Origin: {ORIGIN}","-H","Icy-MetaData: 1","-D","-","-r","0-","--max-filesize","999999999","-o","body.bin","-w","",url])
    h = raw.decode("latin1").lower()
    mi = re.findall(r"^icy-metaint:\s*(\d+)", h, re.M)
    r["metaint"] = int(mi[-1]) if mi else None
    ac = re.findall(r"^access-control-allow-origin:\s*([^\r\n]+)", h, re.M); r["acao"] = ac
    ex = re.findall(r"^access-control-expose-headers:\s*([^\r\n]+)", h, re.M); r["expose"] = ex[-1] if ex else None
    fu = re.findall(r"^location:\s*([^\r\n]+)", h, re.M); r["redirects"] = len(fu)
    title = None
    try:
        b = open("body.bin","rb").read()
        if r["metaint"] and len(b) > r["metaint"]:
            L = b[r["metaint"]] * 16
            meta = b[r["metaint"]+1 : r["metaint"]+1+L].decode("utf-8","replace")
            title = meta.strip("\x00")
    except Exception: pass
    r["icy_meta"] = title
    # icecast status json
    p = urllib.parse.urlparse(url)
    base = f"{p.scheme}://{p.netloc}"
    sj = sh(["curl","-sS","-L","--max-time","6","-A",UA,"-H",f"Origin: {ORIGIN}","-D","-",base+"/status-json.xsl"]).decode("utf-8","replace")
    parts = sj.split("\r\n\r\n")
    sh_ac = re.findall(r"(?im)^access-control-allow-origin:\s*([^\r\n]+)", sj)
    body = parts[-1] if parts else ""
    st_title = None
    try:
        j = json.loads(body); src = j["icestats"].get("source", [])
        if isinstance(src, dict): src = [src]
        mount = p.path
        for s in src:
            lu = s.get("listenurl","")
            if lu.endswith(mount) or mount.endswith(lu.rsplit("/",1)[-1]):
                st_title = s.get("title") or s.get("yp_currently_playing"); break
        r["status_sources"] = len(src)
    except Exception: pass
    r["status_acao"] = sh_ac; r["status_title"] = st_title
    print(json.dumps(r, ensure_ascii=False), flush=True)
# rerun
# rerun 2
