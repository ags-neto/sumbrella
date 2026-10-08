https://youtu.be/7n7HcTeeHdM

## Configuration

The WiFi credentials are **not** stored in the repository. The sketch
`Fetch_rain/Fetch_rain.ino` includes a non-versioned header `secrets.h`
that defines `WIFI_SSID` and `WIFI_PASSWORD`:

```bash
cp Fetch_rain/secrets.h.example Fetch_rain/secrets.h
# edit Fetch_rain/secrets.h with your own network name and password
```

`secrets.h` is listed in `.gitignore`, so it is never committed. The
sketch does not compile without it. If the old password was ever
pushed, change it on the router as well as in `secrets.h`.

`secrets.h` also defines the three ThingHTTP API keys used by the daily
scheduled channels (`THINGHTTP_KEY_TODAY`, `THINGHTTP_KEY_TMRW`,
`THINGHTTP_KEY_AFTMRW`). They used to be hard-coded in the sketch; the old
values were committed, so they must be regenerated in ThingHTTP.
