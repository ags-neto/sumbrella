#!/usr/bin/env python3
"""Offline checks: no credential leaks and a complete secrets.h.example.

Failure conditions (each one makes this script exit non-zero):
  1. Fetch_rain/secrets.h is tracked by git.
  2. Fetch_rain/secrets.h is not covered by .gitignore.
  3. Fetch_rain/secrets.h.example is missing, or does not define every
     WIFI_*/THINGHTTP_KEY_* symbol that Fetch_rain.ino references.
  4. Fetch_rain/secrets.h.example holds anything that does not look like a
     placeholder.
  5. Any git-tracked file holds a literal value for a credential-looking key
     (api_key / password / passwd / pwd / ssid / secret / token), quoted or
     not. A value that is a SCREAMING_SNAKE_CASE identifier is treated as a
     reference to a symbol, not as a literal.

Run with --selftest to prove those checks actually bite: the checker is re-run
against deliberately broken copies and MUST fail on each one.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKETCH = os.path.join("Fetch_rain", "Fetch_rain.ino")
EXAMPLE = os.path.join("Fetch_rain", "secrets.h.example")
SECRETS = os.path.join("Fetch_rain", "secrets.h")

SYMBOL_RE = re.compile(r"\b((?:WIFI|THINGHTTP_KEY)_[A-Z0-9_]+)\b")
KEY = r"(api[_-]?key|password|passwd|pwd|ssid|secret|token)"
QUOTED_RE = re.compile(KEY + r"""\s*[=:]\s*["']([^"'\n]{6,})["']""", re.I)
BARE_RE = re.compile(KEY + r"\s*[=:]\s*([A-Za-z0-9_\-\.]{8,})", re.I)
SYMBOL_VALUE_RE = re.compile(r"^[A-Z0-9_]+$")
PLACEHOLDER_HINTS = ("your-", "your_", "example", "changeme", "change-me",
                     "xxx", "todo", "placeholder", "<", "$", "{}")
SKIP_SUFFIX = (".jpg", ".jpeg", ".png", ".pdf", ".gif", ".ico", ".zip")


def read(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as fh:
        return fh.read()


def git(root, *args):
    return subprocess.run(["git", "-C", root, *args], capture_output=True,
                          text=True)


def is_real(value):
    """True if `value` is a literal that must not be in a tracked file."""
    if "(" in value or ")" in value or "+" in value or " " in value:
        return False
    if SYMBOL_VALUE_RE.match(value):
        return False
    return not any(h in value.lower() for h in PLACEHOLDER_HINTS)


def check(root):
    errors = []
    tracked = [p for p in git(root, "ls-files").stdout.splitlines() if p]
    if not tracked:
        return ["%s is not a git checkout with tracked files" % root]

    if SECRETS in tracked:
        errors.append("SECURITY: %s is tracked by git" % SECRETS)
    if git(root, "check-ignore", "-q", SECRETS).returncode != 0:
        errors.append("SECURITY: %s is not matched by .gitignore" % SECRETS)

    if not os.path.isfile(os.path.join(root, EXAMPLE)):
        errors.append("%s is missing" % EXAMPLE)
        example_text = ""
    else:
        example_text = read(root, EXAMPLE)

    used = set(SYMBOL_RE.findall(read(root, SKETCH)))
    defined = set(re.findall(r"^\s*(?:const\s+char\s*\*\s*)?([A-Z0-9_]+)\s*=",
                             example_text, re.MULTILINE))
    missing = sorted(used - defined)
    if missing:
        errors.append("%s does not define %s (used by %s)"
                      % (EXAMPLE, ", ".join(missing), SKETCH))

    for name, value in re.findall(r"\b([A-Z0-9_]+)\s*=\s*\"([^\"]*)\"",
                                  example_text):
        if not any(h in value.lower() for h in PLACEHOLDER_HINTS):
            errors.append("%s looks like a real value, not a placeholder: "
                          "%s = \"%s\"" % (EXAMPLE, name, value))

    for rel in tracked:
        if rel.endswith(SKIP_SUFFIX) or rel == EXAMPLE:
            continue
        try:
            text = read(root, rel)
        except (UnicodeDecodeError, IsADirectoryError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for regex in (QUOTED_RE, BARE_RE):
                for key, value in regex.findall(line):
                    if is_real(value):
                        errors.append("SECURITY: literal %s in %s:%d (%s)"
                                      % (key.lower(), rel, lineno, value))
    return errors


def run_selftest():
    failures = []
    # The literal is assembled at run time so that this file itself does not
    # contain the pattern the checker looks for.
    fake_key = "Th1ngsP34k" + "RealKey" + "0001"

    def temp_copy():
        tmp = tempfile.mkdtemp(prefix="sumbrella-selftest-")
        dst = os.path.join(tmp, "repo")
        shutil.copytree(REPO, dst, symlinks=True)
        return tmp, dst

    def drop_symbol(dst):
        p = os.path.join(dst, EXAMPLE)
        lines = [l for l in open(p, encoding="utf-8")
                 if not l.startswith("const char* THINGHTTP_KEY_TMRW")]
        open(p, "w", encoding="utf-8").writelines(lines)
        shutil.copyfile(p, os.path.join(dst, SECRETS))

    def drop_gitignore_rule(dst):
        p = os.path.join(dst, ".gitignore")
        lines = [l for l in open(p, encoding="utf-8")
                 if l.strip() != "secrets.h"]
        open(p, "w", encoding="utf-8").writelines(lines)

    def inject_literal(dst):
        with open(os.path.join(dst, "README.md"), "a", encoding="utf-8") as fh:
            fh.write("\n<!-- api_key=" + fake_key + " -->\n")

    def remove_example(dst):
        os.remove(os.path.join(dst, EXAMPLE))

    cases = [
        ("secrets.h.example loses one symbol", drop_symbol),
        (".gitignore loses the secrets.h rule", drop_gitignore_rule),
        ("a tracked file gains a literal api_key", inject_literal),
        ("secrets.h.example is deleted", remove_example),
    ]

    for name, mutate in cases:
        tmp, dst = temp_copy()
        try:
            mutate(dst)
            if check(dst):
                print("  PASS  negative case detected: %s" % name)
            else:
                print("  FAIL  negative case NOT detected: %s" % name)
                failures.append(name)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # Control: the untouched copy must be clean, otherwise the negative cases
    # above prove nothing.
    tmp, dst = temp_copy()
    try:
        errs = check(dst)
        if errs:
            print("  FAIL  control copy is not clean: %s" % "; ".join(errs))
            failures.append("control")
        else:
            print("  PASS  control copy is clean")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return failures


def main():
    if "--selftest" in sys.argv:
        print("check_secrets.py --selftest")
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
    print("  PASS  secrets.h untracked and ignored; secrets.h.example defines "
          "every symbol the sketch uses and holds no real value; no tracked "
          "file holds a literal credential")
    return 0


if __name__ == "__main__":
    sys.exit(main())
