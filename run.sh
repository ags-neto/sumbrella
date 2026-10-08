#!/usr/bin/env bash
# Build both targets and run the offline test suite. Exit status != 0 on any
# build error or test failure. No board is needed.
set -uo pipefail
cd "$(dirname "$0")"
exec bash tests/run_tests.sh
