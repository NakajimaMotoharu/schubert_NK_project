#!/usr/bin/env bash
set -euo pipefail

# SCM-005 / RD171 / SS352 §13 / PT-OPS-SBOM-008..013.
# Use a verified Maven repository for the selected source. Run from its worktree root.
if [[ $# -ne 3 || -z ${3:-} ]]; then
  printf 'Usage: %s MODULE MAVEN_REPOSITORY OUTPUT_TIMESTAMP\n' "$0" >&2
  exit 2
fi

case "$1" in
  protocol|storage|bootstrap|api|web|batch) module_dir="src/schubert-nk-$1" ;;
  *)
    printf 'Expected one of the six NK product modules.\n' >&2
    exit 2
    ;;
esac

if [[ ! -x ./mvnw || ! -f pom.xml || ! -f "$module_dir/pom.xml" ]]; then
  printf 'Run from the root of the selected Maven worktree.\n' >&2
  exit 2
fi

repository=$(cd -- "$2" && pwd -P)
timestamp=$3
target="$PWD/$module_dir/target"
if [[ -L "$target" ]]; then
  printf 'The module target directory must belong to this worktree.\n' >&2
  exit 2
fi
mkdir -p -- "$target"
output_directory=$(mktemp -d -- "$target/software-bom.XXXXXXXX")

./mvnw --batch-mode --no-transfer-progress --strict-checksums \
  "-Dmaven.repo.local=$repository" -pl "$module_dir" \
  org.cyclonedx:cyclonedx-maven-plugin:2.9.3:makeBom \
  -DschemaVersion=1.6 -DoutputFormat=json -DoutputName=software-bom \
  "-DoutputDirectory=$output_directory" "-Dproject.build.outputTimestamp=$timestamp" \
  -DincludeCompileScope=true -DincludeProvidedScope=true -DincludeRuntimeScope=true \
  -DincludeTestScope=false -DincludeSystemScope=false -DincludeBomSerialNumber=false \
  -DdetectUnusedForOptionalScope=false -Dcyclonedx.skipAttach=true

if [[ ! -s "$output_directory/software-bom.json" ]]; then
  printf 'The selected Maven goal produced no software BOM.\n' >&2
  exit 1
fi
printf '%s\n' "$output_directory/software-bom.json"
