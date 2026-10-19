import subprocess, sys
sys.path.insert(0, "scripts")
exec(open("scripts/probe_hls.py").read().split("names = [")[0])
exec("def test(u):" + open("scripts/probe_hls.py").read().split("def test(u):")[1].split("for n, items")[0])
G = """
https://stream.live.vc.bbcmedia.co.uk/bbc_world_service
https://a.files.bbci.co.uk/ms6/live/3441A116-B12E-4D2F-ACA8-C1984642FA4B/audio/simulcast/hls/nonuk/pc_hd_abr_v2/ak/bbc_world_service.m3u8
https://a.files.bbci.co.uk/ms6/live/3441A116-B12E-4D2F-ACA8-C1984642FA4B/audio/simulcast/hls/nonuk/audio_syndication_low_sbr_v1/ak/bbc_world_service.m3u8
https://npr-ice.streamguys1.com/live.mp3
https://playerservices.streamtheworld.com/api/livestream-redirect/KPBSFM.mp3
https://rfienanglais64k.ice.infomaniak.ch/rfienanglais-64.mp3
https://dispatcher.rndfnk.com/br/b5aktuell/live/mp3/mid
https://br-radio.ard-mcdn.de/br/radio/b5aktuell/hls/master.m3u8
https://br-radio.ard-mcdn.de/br/radio/b5akt/hls/master.m3u8
https://icecast.ndr.de/ndr/ndrinfo/niedersachsen/mp3/128/stream.mp3
https://ndr-radio.ard-mcdn.de/ndr/radio/ndrinfonds/hls/master.m3u8
https://wdr-wdr5-live.icecast.wdr.de/wdr/wdr5/live/mp3/128/stream.mp3
https://wdr-radio.ard-mcdn.de/wdr/radio/wdr5/hls/master.m3u8
https://dispatcher.rndfnk.com/hr/hrinfo/live/mp3/high
https://hlshr3.akamaized.net/hls/live/2016536/hrinfo/master.m3u8
https://st01.sslstream.dlf.de/dlf/01/128/mp3/stream.mp3
https://dlf-radio.ard-mcdn.de/dlf/radio/dlf/hls/master.m3u8
"""
for u in G.split():
    try:
        if "m3u8" in u: r = test(u)
        else:
            o = subprocess.run(["curl","-sSL","--max-time","5","-A",UA,"-H","Origin: https://wolftronixsd.github.io","-D","-","-o","/dev/null","-w","%{http_code} %{size_download}",u],capture_output=True).stdout.decode("utf-8","replace")
            ct = [l for l in o.lower().splitlines() if l.startswith("content-type") or l.startswith("access-control-allow-origin")]
            r = o.splitlines()[-1] + " " + (ct[-1] if ct else "")
    except Exception as e: r = f"ERR {e}"
    print(u, "->", r, flush=True)
