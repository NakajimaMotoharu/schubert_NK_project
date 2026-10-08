#!/bin/bash
# Same source reactor dependencies; only two selected Test classes run, never whole acceptance.
set -euC
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
test "$#" = 1
[[ "$1" =~ ^[0-9a-f]{40}$ ]]
test "$(git rev-parse HEAD)" = "$1"
test -z "$(git status --porcelain)"
task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg586-access-selected-v1
test ! -e "$task_base"
mkdir -m 700 "$task_base"
export JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export PATH=$JAVA_HOME/bin:$PATH
date --iso-8601=seconds > "$task_base/started"
git rev-parse HEAD > "$task_base/source"
git ls-files src tools pom.xml | LC_ALL=C sort -u | xargs -r -d '\n' sha256sum > "$task_base/source-files.sha256"
python3 -B - "$task_base" <<'PY'
import hashlib,json,pathlib,sys
base=pathlib.Path(sys.argv[1]);old=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg585-access-reactor-v3')
assert (old/'exit').read_bytes()==b'0\n'
manifest=json.loads((old/'manifest.safe.json').read_bytes())
for module,expected in manifest['moduleResults'].items():
 p=pathlib.Path('src')/('schubert-nk-'+module)/'target/jacoco.exec'
 assert hashlib.sha256(p.read_bytes()).hexdigest()==expected['execSha256']
for module in manifest['moduleResults']:
 p=pathlib.Path('src')/('schubert-nk-'+module)/'target/jacoco.exec'
 p.rename(base/('preexisting-'+module+'.exec'))
PY
task_result=0
(
umask 0027
./mvnw -o --no-transfer-progress -Dstyle.color=never -Djansi.force=false -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api,src/schubert-nk-web,src/schubert-nk-batch spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report jar:jar -Dtest=MorningDatabaseAccessContractTest,MorningDatabaseSessionTest -Dsurefire.failIfNoSpecifiedTests=false
) > "$task_base/build.private.log" 2>&1 || task_result=$?
printf '%s\n' "$task_result" > "$task_base/exit"
date --iso-8601=seconds > "$task_base/completed"
sha256sum --check --status "$task_base/source-files.sha256"
test "$(git rev-parse HEAD)" = "$1"
test -z "$(git status --porcelain)"
if test "$task_result" = 0; then
  cp src/schubert-nk-batch/target/jacoco.exec "$task_base/selected-batch.exec"
  cp src/schubert-nk-batch/target/schubert-nk-batch-0.1.0-SNAPSHOT.jar "$task_base/"
  cp src/schubert-nk-batch/target/spotbugsXml.xml "$task_base/"
  cp src/schubert-nk-batch/target/site/jacoco/jacoco.xml "$task_base/"
  for task_class in MorningDatabaseAccessContractTest MorningDatabaseSessionTest; do
    cp "src/schubert-nk-batch/target/surefire-reports/TEST-dev.codex.schubert.nk.batch.repository.$task_class.xml" "$task_base/"
  done
fi
printf 'PG586_SELECTED actualExit=%s sourceUnchanged=true wholeAcceptance=false\n' "$task_result"
exit "$task_result"
