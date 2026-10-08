# sumbrella

Two Arduino sketches for a smart umbrella: an ESP8266 ESP-01 sketch that fetches the rain probability for today, tomorrow and the day after from ThingSpeak over WiFi, and an Arduino Nano sketch that drives a red/green LED from a DS3231 real-time clock.

## What it is

Two independent sketches, in two PlatformIO projects. Neither sketch names its own board in its source; the board is named on the course poster kept in this repository, `Sumbrella.pdf` ("Listagem de material"): *Arduino Nano* and *ESP8226 ESP-01*.

`Fetch_rain/Fetch_rain.ino` (176 lines, ESP8266 ESP-01)

| Lines | What |
|---|---|
| 1-3 | `ESP8266WiFi.h`, `Wire.h`, `LiquidCrystal_I2C.h` |
| 5 | `#include "secrets.h"` — not versioned, see *Requirements* |
| 7 | `LiquidCrystal_I2C lcd(0x27, 16, 2);` |
| 10-11 | `ssid` and `password`, taken from `secrets.h` |
| 13 | `host = "api.thingspeak.com"` |
| 15-37 | `setup()`: serial at 115200 baud, joins the WiFi network and blocks until connected |
| 40-73 | `loop()`: calls `today()`, `tmrw()`, `aftmrw()` in turn and prints each result |
| 91-119, 121-148, 150-176 | one helper per day, identical apart from the ThingHTTP key |

Each helper opens a TCP connection to `api.thingspeak.com:80`, sends `GET /apps/thinghttp/send_request?api_key=<key>` (lines 103, 132, 160), skips 18 lines of response headers, reads the body up to the first `%` and returns it as an `int` (lines 116-118). On a failed connection it returns `-1`, and `loop()` then prints `Something went wrong, resetting...` and calls `setup()` again from inside `loop()` (lines 49, 59, 69). The rain percentages go to the serial port; that is the whole user interface.

`Projeto.ino` (31 lines, Arduino Nano)

- Lines 1-3: `#include <DS3231.h>` and `DS3231 rtc(SDA, SCL)` — SDA/SCL are A4/A5, i.e. pins 18 and 19.
- Lines 6-12 `setup()`: serial at 9600 baud, `rtc.begin()`, pins 5 and 6 as `OUTPUT`.
- Lines 14-26 `loop()`: prints `rtc.getTimeStr()`, takes `hour` out of the `Time` struct returned by `rtc.getTime()`, and calls `rgLed(150, 150)` while `7 < hour < 14` (08:00-13:59), otherwise `rgLed(0, 0)`; one second per iteration.
- Lines 28-31 `rgLed()`: `analogWrite` on pins 5 and 6. Which of the two is the red LED and which is the green one is not stated anywhere in the code or the poster.

Things that are dead or missing — recorded here, deliberately not changed:

- The LCD is never used. `lcd` is constructed on line 7 of `Fetch_rain.ino` and there is not a single `lcd.` call in either sketch. It costs one library dependency and nothing else.
- There is no rain sensor. Every rain value comes from the ThingSpeak HTTP responses; neither sketch reads an analogue or digital sensor.
- Lines 75-90 of `Fetch_rain.ino` are blank.
- The values returned by `today()`, `tmrw()` and `aftmrw()` are printed and discarded; nothing drives the LED from the rain probability, and `Projeto.ino` never reads the network.

## Requirements

- [PlatformIO Core](https://docs.platformio.org/) 6.2.0, on Python 3.13 (tested in a virtualenv; nothing was installed system-wide).
- Internet access on the first build: PlatformIO downloads the `espressif8266` and `atmelavr` platforms, their toolchains, and the two libraries below (about 200 MB).
- No board is needed to build or to run the tests. Flashing needs the Nano on a USB port and the ESP-01 on a 3.3 V serial adapter; nothing here was run on hardware.
- Two external libraries, both declared in `lib_deps`:
  - `marcoschwartz/LiquidCrystal_I2C@1.1.4` — for the unused LCD, from the PlatformIO registry.
  - DS3231 1.01 (Rinky-Dink Electronics, Henning Karlsen) — for `Projeto.ino`. **It is not in the PlatformIO registry**: all 87 registry search hits for "DS3231" were checked and none exposes the `class Time` / `getTimeStr()` / `DS3231(data_pin, sclk_pin)` API this sketch uses. It is therefore pinned in `lib_deps` to the tag `v1.01` of a mirror whose files were verified byte-for-byte identical to the `libs/DS3231` that was removed from this repository. It is CC BY-NC-SA 3.0 and is not redistributed here — see [DEPENDENCIAS.md](DEPENDENCIAS.md).

`Fetch_rain.ino` does not compile without `Fetch_rain/secrets.h`, which is not versioned. Copy the example and fill in your own values:

```bash
cp Fetch_rain/secrets.h.example Fetch_rain/secrets.h
# then edit Fetch_rain/secrets.h: WIFI_SSID, WIFI_PASSWORD and the three
# THINGHTTP_KEY_* values
```

## Install / Build

There is one PlatformIO project per sketch, because PlatformIO only converts a `*.ino` file that sits at the top of its own `src_dir`.

```bash
# canonical copy on the self-hosted Gitea (aneto/sumbrella), mirrored to GitHub:
git clone ssh://git@127.0.0.1:2222/aneto/sumbrella.git
cd sumbrella

python3 -m venv ~/.venvs/platformio
~/.venvs/platformio/bin/pip install platformio
export PATH="$HOME/.venvs/platformio/bin:$PATH"

cp Fetch_rain/secrets.h.example Fetch_rain/secrets.h   # or ./run.sh does it

pio run                 # Projeto.ino     -> Arduino Nano
pio run -d Fetch_rain   # Fetch_rain.ino  -> ESP8266 ESP-01
./run.sh                # both, then the offline test suite
```

## Usage

Upload with `pio run -t upload` (`pio run -d Fetch_rain -t upload` for the ESP-01; it needs `board = esp01_1m` if the module has 1 MB of flash instead of 512 KB). Then read the serial port at the baud rate in `platformio.ini`: 115200 for the ESP-01, 9600 for the Nano (`pio device monitor`).

No board was attached to the machine this was built on, so this is not a captured session — it is the exact shape of the output, taken from the `Serial.print` calls:

```text
Connecting to <ssid>
.....
WiFi connected
IP address:
192.168.1.23

Today: 20
Tomorrow: 45
After tomorrow: 10
```

with `Something went wrong, resetting...` replacing a value when the connection to `api.thingspeak.com` fails, after which `setup()` runs again. `Projeto.ino` prints one line per second, `HH:MM:SS`, and lights the two LEDs on pins 5 and 6 while the hour is 8 to 13.

## Tests

```bash
./run.sh            # equivalent to: pio run && pio run -d Fetch_rain && bash tests/run_tests.sh
```

Everything below runs without hardware and fails the shell (`exit != 0`) on the first real problem. Output of a run on the machine this was written on:

```text
== pio check, ESP8266 ESP-01
Component                                HIGH    MEDIUM    LOW
Fetch_rain.ino                            0        0        7
Total                                     0        4       33
esp8266        cppcheck  PASSED    00:00:00.112

== pio check, Arduino Nano
Component                                                      HIGH    MEDIUM    LOW
Fetch_rain                                                      0        0        7
Fetch_rain/.pio/libdeps/esp8266/LiquidCrystal_I2C               0        4       26
Projeto.ino                                                     0        0        2
Total                                                           0        5       61
nano           cppcheck  PASSED    00:00:00.467

== compile ESP8266 ESP-01 (Fetch_rain.ino)
RAM:   [====      ]  35.4% (used 28972 bytes from 81920 bytes)
Flash: [======    ]  64.5% (used 280119 bytes from 434160 bytes)
   artefact: Fetch_rain/.pio/build/esp8266/firmware.bin (284272 bytes)
   -> PASS

== compile Arduino Nano (Projeto.ino)
RAM:   [=         ]  10.1% (used 206 bytes from 2048 bytes)
Flash: [=         ]  11.4% (used 3508 bytes from 30720 bytes)
   artefact: .pio/build/nano/firmware.hex (9889 bytes)
   -> PASS

== secrets hygiene
  PASS  secrets.h untracked and ignored; secrets.h.example defines every symbol the sketch uses and holds no real value; no tracked file holds a literal credential
   -> PASS

== secrets negative tests
  PASS  negative case detected: secrets.h.example loses one symbol
  PASS  negative case detected: .gitignore loses the secrets.h rule
  PASS  negative case detected: a tracked file gains a literal api_key
  PASS  negative case detected: secrets.h.example is deleted
  PASS  control copy is clean
SELFTEST OK
   -> PASS

== pin validity
  PASS  all pins used are valid and PWM-capable where required
   -> PASS

== pin negative tests
  PASS  negative case detected: pin outside the board range
  PASS  negative case detected: analogWrite on a non-PWM pin
  PASS  negative case detected: ESP8266 Dn pin name in an AVR sketch
  PASS  control copy is clean
SELFTEST OK
   -> PASS

== overall
ALL TESTS PASSED
```

Each run ends with a full compile of both targets and checks that the linked `firmware.bin` and `firmware.hex` really came out, with their size. The static analysis is placed first on purpose: `pio check` empties the build directory and deletes those binaries.

The zero-warning figure is for the two sketches: a clean build prints no warning for `Projeto.ino` or `Fetch_rain.ino`. The DS3231 library itself prints 41 warnings (40 `-Wwrite-strings`, 1 `-Wparentheses`) and `LiquidCrystal_I2C` raises 4 cppcheck `medium` findings; both are third-party and were left alone.

What the suite covers:

- **Compile.** Both targets are built for real, for the board named in `platformio.ini`. A compile error fails the run.
- **Static analysis.** `pio check` on both projects; it fails on any `high` defect.
- **Secrets.** `tests/check_secrets.py` fails if `Fetch_rain/secrets.h` is tracked or is missing from `.gitignore`, if `Fetch_rain/secrets.h.example` is missing or does not define every `WIFI_*`/`THINGHTTP_KEY_*` symbol `Fetch_rain.ino` uses, if the example holds anything that is not a placeholder, or if any tracked file holds a literal value for `api_key`/`password`/`passwd`/`pwd`/`ssid`/`secret`/`token` (quoted or not; a value that is a SCREAMING_SNAKE_CASE identifier counts as a symbol reference, not a literal).
- **Negative cases.** `--selftest` re-runs the same checkers against throwaway copies in which a symbol was deleted from `secrets.h.example`, the `secrets.h` rule was removed from `.gitignore`, a literal key was appended to `README.md`, the example was deleted, a pin was pushed out of range, `analogWrite` was moved to a non-PWM pin, and an ESP8266 `Dn` name was put in an AVR sketch. Each mutation must be detected, and an untouched copy must be clean; if a mutation goes undetected the selftest fails.
- **Pins.** `tests/check_pins.py` resolves every `pinMode`/`digitalWrite`/`digitalRead`/`analogWrite`/`analogRead` argument and the `SDA`/`SCL` macros against the Nano pin map, and checks that `analogWrite` is only used on PWM-capable pins.

Not covered, because it needs hardware: uploading, the WiFi association, the ThingSpeak responses, the I2C conversation with the DS3231, the LCD (which the code never writes to) and the LED behaviour. Nothing here was flashed.

## Structure

```text
Projeto.ino                    Nano + DS3231: 08:00-13:59 window, two LEDs on pins 5 and 6  (31 lines)
Fetch_rain/Fetch_rain.ino      ESP-01: three ThingHTTP GETs, percentages on the serial port     (176 lines)
Fetch_rain/secrets.h.example   the five symbols the sketch needs, with placeholder values       (11 lines)
Fetch_rain/platformio.ini      PlatformIO project for the ESP-01 (src_dir = .)                   (22 lines)
platformio.ini                 PlatformIO project for Projeto.ino (src_dir = .)                  (32 lines)
run.sh                         build both targets, then run the tests                            (6 lines)
tests/run_tests.sh             the suite: pio check, the two compiles, and the two checkers      (74 lines)
tests/check_secrets.py         secrets hygiene, with --selftest for the negative cases          (196 lines)
tests/check_pins.py            pins against the board pin maps, with --selftest                 (170 lines)
DEPENDENCIAS.md                the DS3231 library: origin, version, licence, why it is not here
LICENSE                        MIT
Sumbrella.pdf                  the course poster; the only place the boards are named
Screenshot_6.jpg               photo of the assembly; no code reads it
README.md                      this file
```

Every path above is in the repository. `Fetch_rain/secrets.h` is created from the example, is listed in `.gitignore` and is never committed.

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2020 André Guilherme dos Santos Neto and João Miguel Alves Moitas. `Sumbrella.pdf`, the course poster kept in this repository, names two students as authors of the work (André Guilherme dos Santos Neto and João Miguel Alves Moitas); the `LICENSE` file names only the first of them.

The DS3231 library used by `Projeto.ino` is third-party. It is CC BY-NC-SA 3.0, incompatible with MIT, and for that reason it is not redistributed here: it was removed from `libs/DS3231` and is now declared as an external dependency in [DEPENDENCIAS.md](DEPENDENCIAS.md) and pinned in `lib_deps`. It keeps its own licence, and commercial use of it requires a paid licence from its author (Rinky-Dink Electronics).

The WiFi password and the three ThingHTTP keys are not in the repository and never were: every revision reachable from `main` (six commits, including the `ESP8266_Fetching_Data.ino` sketch that was deleted in `b804d9a`) was scanned for a credential-looking literal and none was found — the old sketch carried the literal string `<REDACTED>` in its place.
