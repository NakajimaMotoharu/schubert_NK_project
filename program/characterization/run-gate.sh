#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
BASE_ROOT="$(dirname -- "$PROJECT_ROOT")"

CURRENT_ROOT="${CHR_CURRENT_ROOT:-$BASE_ROOT/schubert_project}"
WORK_ROOT="${CHR_WORK_ROOT:-$BASE_ROOT/work}"
TOOLS_ROOT="${CHR_TOOLS_ROOT:-$WORK_ROOT/characterization-tools}"
RUNTIME_BASE="${CHR_RUNTIME_BASE:-$WORK_ROOT/characterization-runtime}"
REPORT_BASE="${CHR_REPORT_BASE:-$SCRIPT_DIR/reports/current}"
BASELINE_ROOT="${CHR_BASELINE_ROOT:-$SCRIPT_DIR/baseline/current}"

JAVA_HOME="${JAVA_HOME:-$TOOLS_ROOT/root/usr/lib/jvm/java-25-openjdk-amd64}"
JAVA_EXECUTABLE="${CHR_JAVA_EXECUTABLE:-$JAVA_HOME/bin/java}"
CADDY_EXECUTABLE="${CHR_CADDY_EXECUTABLE:-$TOOLS_ROOT/root/usr/bin/caddy}"
CURRENT_JAR="${CHR_CURRENT_JAR:-$CURRENT_ROOT/program/app/target/schubert-0.1.0.jar}"
ASSET_ROOT="${CHR_ASSET_ROOT:-$CURRENT_ROOT/data/master}"
USERS_FILE="${CHR_USERS_FILE:-$RUNTIME_BASE/credentials/current-users.txt}"
DB_URL="${CHR_DB_URL:-jdbc:postgresql://127.0.0.1:55432/scenario_search_chr}"
DB_USER="${CHR_DB_USER:-scenario_app}"
APP_PORT="${CHR_APP_PORT:-46962}"
PROXY_PORT="${CHR_PROXY_PORT:-55162}"

if [[ -x "$TOOLS_ROOT/apache-maven-3.9.12/bin/mvn" ]]; then
  MAVEN="$TOOLS_ROOT/apache-maven-3.9.12/bin/mvn"
else
  MAVEN="$PROJECT_ROOT/mvnw"
fi

export JAVA_HOME
export PATH="$JAVA_HOME/bin:$PATH"
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-$TOOLS_ROOT/playwright-browsers}"
export PLAYWRIGHT_HOST_PLATFORM_OVERRIDE="${PLAYWRIGHT_HOST_PLATFORM_OVERRIDE:-ubuntu24.04-x64}"
export MAVEN_OPTS="${MAVEN_OPTS:-} -Djavax.net.ssl.trustStore=$TOOLS_ROOT/root/etc/ssl/certs/java/cacerts -Djavax.net.ssl.trustStorePassword=changeit -Djavax.net.ssl.trustStoreType=PKCS12"

MAVEN_COMMON=(
  -q
  "-Dmaven.repo.local=$TOOLS_ROOT/m2"
  -pl program/characterization
  "-Dchr.projectRoot=$PROJECT_ROOT"
  "-Dchr.currentRoot=$CURRENT_ROOT"
  "-Dchr.currentJar=$CURRENT_JAR"
  "-Dchr.assetRoot=$ASSET_ROOT"
  "-Dchr.usersFile=$USERS_FILE"
  "-Dchr.javaExecutable=$JAVA_EXECUTABLE"
  "-Dchr.caddyExecutable=$CADDY_EXECUTABLE"
  "-Dchr.runtimeRoot=$RUNTIME_BASE/preflight"
  "-Dchr.dbUrl=$DB_URL"
  "-Dchr.dbUser=$DB_USER"
  "-Dchr.appPort=$APP_PORT"
  "-Dchr.proxyPort=$PROXY_PORT"
)

usage() {
  printf '%s\n' \
    "Usage: $0 verify-source|preflight|install-browser" \
    "       $0 capture-current <run-id>" \
    "       $0 compare-current <first-run-id> <second-run-id>" \
    "       $0 report <first-run-id> <second-run-id>" \
    "       $0 promote-current <run-id>"
}

run_cli() {
  local arguments="$1"
  "$MAVEN" "${MAVEN_COMMON[@]}" \
    -Dexec.mainClass=dev.codex.schubert.characterization.GateCli \
    -Dexec.classpathScope=compile \
    "-Dexec.args=$arguments" \
    exec:java
}

require_new_directory() {
  local target="$1"
  if [[ -e "$target" ]]; then
    printf 'Refusing to overwrite existing evidence: %s\n' "$target" >&2
    exit 2
  fi
  mkdir -p "$target"
}

command_name="${1:-}"
case "$command_name" in
  verify-source)
    mkdir -p "$SCRIPT_DIR/reports"
    run_cli "verify-source $SCRIPT_DIR/reports/source-verification.json"
    ;;
  preflight)
    mkdir -p "$SCRIPT_DIR/reports"
    run_cli "preflight $SCRIPT_DIR/reports/preflight.json"
    ;;
  install-browser)
    "$MAVEN" "${MAVEN_COMMON[@]}" \
      -Dexec.classpathScope=test \
      -Dexec.mainClass=com.microsoft.playwright.CLI \
      -Dexec.args='install chromium' \
      exec:java
    ;;
  capture-current)
    run_id="${2:?run-id is required}"
    output_root="$REPORT_BASE/$run_id"
    runtime_root="$RUNTIME_BASE/$run_id"
    require_new_directory "$output_root"
    mkdir -p "$runtime_root"
    "$MAVEN" "${MAVEN_COMMON[@]}" \
      "-Dchr.runtimeRoot=$runtime_root" \
      "-Dchr.output=$output_root" \
      -Dtest=GateContractTest,CurrentCharacterizationTest \
      test
    ;;
  compare-current)
    first_id="${2:?first-run-id is required}"
    second_id="${3:?second-run-id is required}"
    mkdir -p "$SCRIPT_DIR/reports"
    run_cli "compare-current $REPORT_BASE/$first_id $REPORT_BASE/$second_id $SCRIPT_DIR/reports/current-repeat-comparison.json"
    ;;
  report)
    first_id="${2:?first-run-id is required}"
    second_id="${3:?second-run-id is required}"
    run_cli "report $REPORT_BASE/$first_id $REPORT_BASE/$second_id $SCRIPT_DIR/reports/current-repeat-comparison.json $SCRIPT_DIR/reports/gate-report.json"
    ;;
  promote-current)
    run_id="${2:?run-id is required}"
    run_cli "promote-current $REPORT_BASE/$run_id $BASELINE_ROOT"
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
