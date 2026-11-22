#!/usr/bin/env bash
set -euo pipefail

# SCM-005 / RD171 / SS352 / SS354 / PT-OPS-CI-PRO001..004.
if [[ $# -ne 1 ]]; then
  printf 'Usage: %s MAVEN_REPOSITORY\n' "$0" >&2
  exit 2
fi

module=src/schubert-nk-protocol
if [[ ! -x ./mvnw || ! -f pom.xml || ! -f "$module/pom.xml" ]]; then
  printf 'Run from the root of the selected Maven worktree.\n' >&2
  exit 2
fi

if [[ ! -d "$1" ]]; then
  printf 'The Maven repository must already exist.\n' >&2
  exit 2
fi

repository=$(cd -- "$1" && pwd -P)
unset MAVEN_ARGS
exec ./mvnw --offline --batch-mode --strict-checksums --no-transfer-progress \
  "-Dmaven.repo.local=$repository" -DskipTests=false -Dmaven.test.skip=false \
  -Dmaven.test.failure.ignore=false -DfailIfNoTests=true -pl "$module" verify
