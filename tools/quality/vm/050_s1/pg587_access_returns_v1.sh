#!/bin/bash
# Selected natural default return dispatch; installed dependencies pinned by PG586, no VM actions.
set -euC
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
test "$#" = 1 -o "$#" = 2
[[ "$1" =~ ^[0-9a-f]{40}$ ]]
test "$(git rev-parse HEAD)" = "$1"
test -z "$(git status --porcelain)"
task_profile=${2:-PG587}
case "$task_profile" in
  PG587)
    task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg587-access-returns-v1
    task_prior=pg586-access-selected-v3
    ;;
  PG588)
    task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg588-session-readback-v1
    task_prior=pg587-access-returns-v1
    ;;
  PG588V2)
    task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg588-session-readback-v2
    task_prior=pg587-access-returns-v1
    ;;
  PG589)
    task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg589-session-sql-close-v1
    task_prior=pg588-session-readback-v2
    ;;
  PG590)
    task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg590-cleanup-expiry-db-v1
    task_prior=pg589-session-sql-close-v1
    ;;
  PG592)
    task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg592-session-transition-faults-v1
    task_prior=pg590-cleanup-expiry-db-v1
    ;;
  PG592V2)
    task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg592-session-transition-faults-v2
    task_prior=pg590-cleanup-expiry-db-v1
    ;;
  *) exit 2 ;;
esac
test ! -e "$task_base"
mkdir -m 700 "$task_base"
export JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export PATH=$JAVA_HOME/bin:$PATH
date --iso-8601=seconds > "$task_base/started"
git rev-parse HEAD > "$task_base/source"
git ls-files src tools pom.xml | LC_ALL=C sort -u | xargs -r -d '\n' sha256sum > "$task_base/source-files.sha256"
python3 -B - "$task_base" "$task_prior" "$task_profile" <<'PY'
import hashlib,json,pathlib,sys,zipfile
base=pathlib.Path(sys.argv[1]);w=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
assert sys.argv[2]in ('pg586-access-selected-v3','pg587-access-returns-v1','pg588-session-readback-v2','pg589-session-sql-close-v1','pg590-cleanup-expiry-db-v1')
old=w/sys.argv[2];manifest=json.loads((old/'manifest.safe.json').read_bytes())
assert manifest['actualExit']==0 and manifest['mainClassBytesEqualInstalledCurrentPG585']==1600
for module in ('protocol','storage','bootstrap','api','web','batch'):
 name='schubert-nk-'+module;jar=name+'-0.1.0-SNAPSHOT.jar';values=[]
 for p in (w/'pg585-access-reactor-v3'/module/jar,pathlib.Path('src')/name/'target'/jar,pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository/dev/codex/schubert')/name/'0.1.0-SNAPSHOT'/jar):
  with zipfile.ZipFile(p)as z:values.append({n:z.read(n)for n in z.namelist()if n.endswith('.class')})
 assert values[0]==values[1]==values[2]and values[0]
p=pathlib.Path('src/schubert-nk-batch/target/jacoco.exec')
expected=manifest['selectedExecSha256']
if sys.argv[3]=='PG588V2':
 failed=w/'pg588-session-readback-v1'
 assert (failed/'source').read_text().strip()=='4f03d7af68a5d2d942104ca649859675fc405987' and (failed/'exit').read_bytes()==b'1\n'
 expected=hashlib.sha256((failed/'failed-batch.exec').read_bytes()).hexdigest()
if sys.argv[3]=='PG592V2':
 failed=w/'pg592-session-transition-faults-v1'
 assert (failed/'source').read_text().strip()=='678ae3a396092a99978c7c15e6f101f92123c999' and (failed/'exit').read_bytes()==b'1\n'
 expected=hashlib.sha256((failed/'failed-batch.exec').read_bytes()).hexdigest()
assert hashlib.sha256(p.read_bytes()).hexdigest()==expected;p.rename(base/'preexisting-selected-batch.exec')
PY
task_result=0
(
umask 0027
./mvnw -o --no-transfer-progress -Dstyle.color=never -Djansi.force=false -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-batch spotless:check test-compile test spotbugs:check jacoco:report jar:jar -Dtest=MorningDatabaseAccessContractTest,MorningDatabaseSessionTest
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
printf '%s_SELECTED actualExit=%s sourceUnchanged=true wholeAcceptance=false\n' "$task_profile" "$task_result"
exit "$task_result"
