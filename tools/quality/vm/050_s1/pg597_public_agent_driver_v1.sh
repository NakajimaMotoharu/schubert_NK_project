#!/bin/bash
# Bootstrap-only changed Production candidate. Installed VM source remains969, never relabel it.
set -euC
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
test "$#" = 1 -o "$#" = 2
[[ "$1" =~ ^[0-9a-f]{40}$ ]]
test "$(git rev-parse HEAD)" = "$1"
test -z "$(git status --porcelain)"
case "${2:-v1}" in
  v1) task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg597-public-agent-driver-v1 ;;
  v2) task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg597-public-agent-driver-v2 ;;
  v3) task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg597-public-agent-driver-v3 ;;
  PG598) task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg598-ordinary-process-policy-v1 ;;
  PG598V2) task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg598-ordinary-process-policy-v2 ;;
  *) exit 2 ;;
esac
test ! -e "$task_base"
mkdir -m 700 "$task_base"
export JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export PATH=$JAVA_HOME/bin:$PATH
date --iso-8601=seconds > "$task_base/started"
git rev-parse HEAD > "$task_base/source"
git ls-files src tools pom.xml | LC_ALL=C sort -u | xargs -r -d '\n' sha256sum > "$task_base/source-files.sha256"
python3 -B - "$task_base" "${2:-v1}" <<'PY'
import hashlib,json,pathlib,sys,zipfile
w=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');old=w/'pg596-fixture-retained-six-host-v1'
assert hashlib.sha256((old/'manifest.safe.json').read_bytes()).hexdigest()=='a91fd3f455aa79b64f32a971b9a4757ca62b58d31e93c3627c394f5a703570f1'
proof=json.loads((old/'manifest.safe.json').read_bytes());assert proof['actualExit']==0 and proof['tests']==3450
for module in ('protocol','storage','bootstrap','api','web','batch'):
 name='schubert-nk-'+module;jar=name+'-0.1.0-SNAPSHOT.jar';a=[]
 for p in (old/module/jar,pathlib.Path('src')/name/'target'/jar,pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository/dev/codex/schubert')/name/'0.1.0-SNAPSHOT'/jar):
  with zipfile.ZipFile(p)as z:a.append({n:z.read(n)for n in z.namelist()if n.endswith('.class')})
 if sys.argv[2]in ('v3','PG598','PG598V2') and module=='bootstrap':
  selected=w/('pg597-public-agent-driver-v2' if sys.argv[2]=='v3' else 'pg597-public-agent-driver-v3')
  digest='0e1e4dda99bd901da2471f619cf7afc878f96d5581335a1f048881c9dddb1214' if sys.argv[2]=='v3' else '03a51266e880357b55e4c1f0809962324da8a228cabd6580de2656bee13bea6b'
  assert hashlib.sha256((selected/'manifest.safe.json').read_bytes()).hexdigest()==digest
  selected_proof=json.loads((selected/'manifest.safe.json').read_bytes());assert selected_proof['actualExit']==0 and selected_proof['selectedTests']==(26 if sys.argv[2]=='v3' else 27)
  with zipfile.ZipFile(selected/jar)as z:current={n:z.read(n)for n in z.namelist()if n.endswith('.class')}
  assert a[0]==a[2] and a[1]==current and a[0]
 else:assert a[0]==a[1]==a[2]and a[0]
if sys.argv[2]=='v1':
 p=pathlib.Path('src/schubert-nk-bootstrap/target/jacoco.exec')
 assert hashlib.sha256(p.read_bytes()).hexdigest()==proof['moduleResults']['bootstrap']['execSha256']
 p.rename(pathlib.Path(sys.argv[1])/'preexisting-bootstrap.exec')
elif sys.argv[2]=='v2':
 failed=w/'pg597-public-agent-driver-v1';assert (failed/'exit').read_bytes()==b'1\n'
 log=(failed/'build.private.log').read_text();assert 'COMPILATION ERROR'in log and 'testCompile'in log
 assert not pathlib.Path('src/schubert-nk-bootstrap/target/jacoco.exec').exists()
 assert hashlib.sha256((failed/'preexisting-bootstrap.exec').read_bytes()).hexdigest()==proof['moduleResults']['bootstrap']['execSha256']
elif sys.argv[2]in ('v3','PG598'):
 p=pathlib.Path('src/schubert-nk-bootstrap/target/jacoco.exec')
 assert hashlib.sha256(p.read_bytes()).hexdigest()==selected_proof['execSha256']
 p.rename(pathlib.Path(sys.argv[1])/'preexisting-bootstrap.exec')
else:
 failed=w/'pg598-ordinary-process-policy-v1'
 assert (failed/'exit').read_bytes()==b'1\n' and 'COMPILATION ERROR'in (failed/'build.private.log').read_text()
 assert not pathlib.Path('src/schubert-nk-bootstrap/target/jacoco.exec').exists()
 assert hashlib.sha256((failed/'preexisting-bootstrap.exec').read_bytes()).hexdigest()==selected_proof['execSha256']
PY
task_result=0
(
umask 0027
python3 -B tools/quality/qualified_nullable_check.py &&
./mvnw -o --no-transfer-progress -Dstyle.color=never -Djansi.force=false -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-bootstrap spotless:check test-compile test spotbugs:check jacoco:report jar:jar -Dtest=FixedNativeCoverageCheckpointTest,FixedNativeCoverageProfileTest,NativeCoveragePrivateFileTest,FixedNativeCoverageStopHoldTest
) > "$task_base/build.private.log" 2>&1 || task_result=$?
printf '%s\n' "$task_result" > "$task_base/exit"
date --iso-8601=seconds > "$task_base/completed"
sha256sum --check --status "$task_base/source-files.sha256"
test "$(git rev-parse HEAD)" = "$1"
test -z "$(git status --porcelain)"
if test "$task_result" = 0; then
  cp src/schubert-nk-bootstrap/target/jacoco.exec "$task_base/bootstrap.exec"
  cp src/schubert-nk-bootstrap/target/schubert-nk-bootstrap-0.1.0-SNAPSHOT.jar "$task_base/"
  cp src/schubert-nk-bootstrap/target/spotbugsXml.xml "$task_base/"
  cp src/schubert-nk-bootstrap/target/site/jacoco/jacoco.xml "$task_base/"
  for task_class in FixedNativeCoverageCheckpointTest FixedNativeCoverageProfileTest NativeCoveragePrivateFileTest FixedNativeCoverageStopHoldTest; do
    cp "src/schubert-nk-bootstrap/target/surefire-reports/TEST-dev.codex.schubert.nk.bootstrap.$task_class.xml" "$task_base/"
  done
fi
printf 'PG597_SELECTED actualExit=%s candidateSourceUnchanged=true vmDeployment0=true formalAccepted=false\n' "$task_result"
exit "$task_result"
