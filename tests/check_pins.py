#!/usr/bin/env python3
"""Offline check: every MCU pin used by the sketches exists on the target board.

Board data is the published pin map of each board:

- Arduino Nano (ATmega328P, DIP-30): digital pins 0-19, where A0-A5 are 14-19,
  PWM on 3, 5, 6, 9, 10 and 11, and SDA/SCL are A4/A5 = 18/19.
- ESP-01 (ESP8266EX, 8-pin module): GPIO0-GPIO3 are the pins broken out; PWM is
  available on every ESP8266 GPIO except GPIO16.

The board of each sketch is the one named on the course poster kept in this
repository (Sumbrella.pdf, "Listagem de material": Arduino Nano and ESP8266
ESP-01) and declared in platformio.ini.

Run with --selftest to prove the check bites: copies with an out-of-range pin
and with analogWrite() on a non-PWM pin must both be rejected.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BOARDS = {
    "nano": {
        "env": "nano",
        "sketch": "Projeto.ino",
        "pins": set(range(0, 20)),
        "pwm": {3, 5, 6, 9, 10, 11},
        "macros": {"SDA": 18, "SCL": 19},
        "dn_pins": False,
    },
    "esp01": {
        "env": "esp8266",
        "sketch": os.path.join("Fetch_rain", "Fetch_rain.ino"),
        "pins": {0, 1, 2, 3},
        "pwm": {0, 1, 2, 3},
        "macros": {},
        "dn_pins": True,
    },
}

CALL_RE = re.compile(
    r"\b(pinMode|digitalWrite|digitalRead|analogWrite|analogRead)\s*\(\s*"
    r"([A-Za-z_][A-Za-z0-9_]*|\d+)"
)
ESPNUM_RE = re.compile(r"\bD(\d{1,2})\b")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def used_pins(text, macros):
    """Return [(function, raw_pin_text, resolved_int)] for a sketch."""
    found = []
    for func, raw in CALL_RE.findall(text):
        if raw.isdigit():
            found.append((func, raw, int(raw)))
        elif raw in macros:
            found.append((func, raw, macros[raw]))
    return found


def check(root):
    errors = []
    for board, cfg in BOARDS.items():
        path = os.path.join(root, cfg["sketch"])
        if not os.path.isfile(path):
            errors.append("%s: sketch %s is missing" % (board, cfg["sketch"]))
            continue
        text = read(path)

        for func, raw, pin in used_pins(text, cfg["macros"]):
            if pin not in cfg["pins"]:
                errors.append("%s: %s(%s) -> pin %s does not exist on %s "
                              "(valid: 0-%d)"
                              % (board, func, raw, pin, board,
                                 max(cfg["pins"])))
            elif func == "analogWrite" and pin not in cfg["pwm"]:
                errors.append("%s: analogWrite(%s) -> pin %s is not PWM-capable"
                              % (board, raw, pin))

        # A stray D0..D16 style pin on the AVR target would not compile.
        if not cfg["dn_pins"] and ESPNUM_RE.search(text):
            errors.append("%s: %s uses an ESP8266 Dn pin name"
                          % (board, cfg["sketch"]))
    return errors


def run_selftest():
    failures = []

    def copy():
        tmp = tempfile.mkdtemp(prefix="sumbrella-pin-selftest-")
        dst = os.path.join(tmp, "repo")
        shutil.copytree(REPO, dst, symlinks=True)
        return tmp, dst

    cases = [
        ("pin outside the board range",
         "Projeto.ino",
         lambda t: t.replace("pinMode(5, OUTPUT)", "pinMode(23, OUTPUT)")),
        ("analogWrite on a non-PWM pin",
         "Projeto.ino",
         lambda t: t.replace("analogWrite(5, redValue)",
                             "analogWrite(4, redValue)")),
        ("ESP8266 Dn pin name in an AVR sketch",
         "Projeto.ino",
         lambda t: t.replace("pinMode(6, OUTPUT)", "pinMode(D6, OUTPUT)")),
    ]

    for name, rel, mutate in cases:
        tmp, dst = copy()
        try:
            p = os.path.join(dst, rel)
            text = read(p)
            new = mutate(text)
            if new == text:
                print("  FAIL  selftest could not mutate %s (%s)" % (rel, name))
                failures.append(name)
                continue
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(new)
            if check(dst):
                print("  PASS  negative case detected: %s" % name)
            else:
                print("  FAIL  negative case NOT detected: %s" % name)
                failures.append(name)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    tmp, dst = copy()
    try:
        if check(dst):
            print("  FAIL  control copy is not clean: %s" % "; ".join(check(dst)))
            failures.append("control")
        else:
            print("  PASS  control copy is clean")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return failures


def main():
    if "--selftest" in sys.argv:
        print("check_pins.py --selftest")
        failures = run_selftest()
        if failures:
            print("SELFTEST FAILED: %s" % ", ".join(failures))
            return 1
        print("SELFTEST OK")
        return 0

    errors = check(REPO)
    for err in errors:
        print("  FAIL  %s" % err)
    if errors:
        return 1
    print("  PASS  all pins used are valid and PWM-capable where required")
    return 0


if __name__ == "__main__":
    sys.exit(main())
