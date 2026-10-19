import subprocess, sys
sys.path.insert(0, "scripts")
exec(open("scripts/probe_hls.py").read().split("names = [")[0])
exec("def test(u):" + open("scripts/probe_hls.py").read().split("def test(u):")[1].split("for n, items")[0])
G = """
https://swr-radio.ard-mcdn.de/swr/radio/swr3/hls/master.m3u8
https://swr-radio.ard-mcdn.de/swr/radio/swr3/hls/96/seglist.m3u8
https://swrswr3-hls.akamaized.net/hls/live/2018681/swr3/master.m3u8
https://liveradio.swr.de/sw73hl2/swr3/play.m3u8
https://liveradio.swr.de/sw73hl2/swr1bw/play.m3u8
https://swrswr1bw-hls.akamaized.net/hls/live/2018673/swr1bw/master.m3u8
https://ndr-radio.ard-mcdn.de/ndr/radio/ndr2/niedersachsen/hls/master.m3u8
https://ndr-ndr2-niedersachsen.akamaized.net/hls/live/2018230/ndr2nds/master.m3u8
https://ndr-radio.ard-mcdn.de/ndr/radio/ndr2/hls/master.m3u8
https://dlf-radio.ard-mcdn.de/dlf/radio/dlf/hls/master.m3u8
https://dradio-dlf-live.cast.addradio.de/dradio/dlf/live/aac/high/stream.aac
https://st01.sslstream.dlf.de/dlf/01/high/aac/stream.aac
https://wdr-radio.ard-mcdn.de/wdr/radio/1live/hls/master.m3u8
https://hlshr3.akamaized.net/hls/live/2016536/hr3rheinmain/master.m3u8
https://br-radio.ard-mcdn.de/br/radio/b3/hls/96/seglist.m3u8
https://br-radio.ard-mcdn.de/br/radio/b1obb/hls/96/seglist.m3u8
https://ice2.somafm.com/u80s-64-aac
https://ice2.somafm.com/u80s-128-aac
https://listen.181fm.com/181-awesome80s_64k.aac
https://streams.bigfm.de/bigfm-workout-64-aac
https://stream.antenne.de/antenne/stream/aac
https://stream.rockantenne.de/rockantenne/stream/aac
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
