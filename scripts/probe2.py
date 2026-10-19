import subprocess, sys
sys.path.insert(0, "scripts")
exec(open("scripts/probe_hls.py").read().split("names = [")[0])
exec("def test(u):" + open("scripts/probe_hls.py").read().split("def test(u):")[1].split("for n, items")[0])
G = """
https://swr-radio.ard-mcdn.de/swr/radio/swr1bw/hls/master.m3u8
https://swr-radio.ard-mcdn.de/swr/radio/swr1/hls/master.m3u8
https://ndr-radio.ard-mcdn.de/ndr/radio/ndr2nds/hls/master.m3u8
https://ndr-radio.ard-mcdn.de/ndr/radio/ndr2_nds/hls/master.m3u8
https://ndr-radio.ard-mcdn.de/ndr/radio/ndr2-niedersachsen/hls/master.m3u8
https://br-radio.ard-mcdn.de/br/radio/b3/hls/master.m3u8
"""
for u in G.split():
    try:
        if "m3u8" in u: r = test(u)
        else:
            o = subprocess.run(["curl","-sSL","--max-time","5","-A",UA,"-D","-","-o","/dev/null","-w","%{http_code} %{size_download}",u],capture_output=True).stdout.decode("utf-8","replace")
            ct = [l for l in o.lower().splitlines() if l.startswith("content-type")]
            r = o.splitlines()[-1] + " " + (ct[-1] if ct else "")
    except Exception as e: r = f"ERR {e}"
    print(u, "->", r, flush=True)
