import json, urllib.request, urllib.parse, subprocess
def api(path, **q):
    url = "https://de1.api.radio-browser.info/json/" + path + "?" + urllib.parse.urlencode(q)
    req = urllib.request.Request(url, headers={"User-Agent": "WRadio-probe/1.0"})
    return json.load(urllib.request.urlopen(req, timeout=20))
seen = {}
for q in [dict(tag="80s"), dict(tag="80er"), dict(tag="commercial free"), dict(tag="no ads"), dict(name="80s forever"), dict(name="made in 80"),
          dict(name="nightride"), dict(name="underground 80s"), dict(name="80er revival"), dict(name="80er kulthits"), dict(name="seefunk 80er"), dict(tag="synthpop")]:
    try:
        for s in api("stations/search", order="votes", reverse="true", limit=40, hidebroken="true", **q):
            seen[s["stationuuid"]] = s
    except Exception as e:
        print("ERR", q, e)
rows = sorted(seen.values(), key=lambda s: -s["votes"])
for s in rows:
    t = s["tags"].lower()
    if "80" not in t + s["name"].lower() and "commercial" not in t and "no ads" not in t: continue
    print(f'{s["votes"]:>6} {s["codec"]:<5}{s["bitrate"]:>4} {s["countrycode"]} | {s["name"][:45]} | {s["url_resolved"]} | {s["tags"][:80]} | {s["homepage"]}')
