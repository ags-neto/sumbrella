#!/usr/bin/env bash
# Offline test suite for sumbrella. Exit status != 0 if anything fails.
# Nothing here needs a board: it is a real compile for both targets plus
# static analysis of the sources. See README.md, section "Tests".
#
# The static analysis runs first on purpose: `pio check` triggers a clean build
# and removes firmware.bin/firmware.elf/firmware.hex, so the real compiles come
# last and leave the linked binaries in place.
set -uo pipefail
cd "$(dirname "$0")/.."

PIO="${PIO:-}"
if [ -z "$PIO" ]; then
  for c in "$(command -v pio || true)" "$HOME/.venvs/platformio/bin/pio"; do
    [ -n "$c" ] && [ -x "$c" ] && PIO="$c" && break
  done
fi

if [ ! -f Fetch_rain/secrets.h ]; then
  cp Fetch_rain/secrets.h.example Fetch_rain/secrets.h
fi

rc=0
run() {
  local name="$1"; shift
  echo "== $name"
  if "$@"; then
    echo "   -> PASS"
  else
    echo "   -> FAIL"
    rc=1
  fi
  echo
}

build() {
  local name="$1" dir="$2" artefact="$3"
  echo "== $name"
  if "$PIO" run ${dir:+-d "$dir"}; then
    if [ -f "$artefact" ]; then
      echo "   artefact: $artefact ($(stat -c%s "$artefact") bytes)"
    else
      echo "   artefact missing: $artefact"
      rc=1
    fi
    echo "   -> PASS"
  else
    echo "   -> FAIL"
    rc=1
  fi
  echo
}

if [ -n "$PIO" ]; then
  run "pio check, ESP8266 ESP-01" "$PIO" check -d Fetch_rain --skip-packages
  run "pio check, Arduino Nano" "$PIO" check --skip-packages
  build "compile ESP8266 ESP-01 (Fetch_rain.ino)" "Fetch_rain" \
        "Fetch_rain/.pio/build/esp8266/firmware.bin"
  build "compile Arduino Nano (Projeto.ino)" "" \
        ".pio/build/nano/firmware.hex"
else
  echo "== compile + static analysis: SKIPPED (no pio on PATH or in ~/.venvs/platformio)"
  echo
  rc=1
fi

run "secrets hygiene"        python3 tests/check_secrets.py
run "secrets negative tests" python3 tests/check_secrets.py --selftest
run "pin validity"           python3 tests/check_pins.py
run "pin negative tests"     python3 tests/check_pins.py --selftest

echo "== overall"
if [ "$rc" -eq 0 ]; then echo "ALL TESTS PASSED"; else echo "TESTS FAILED"; fi
exit "$rc"
