#!/bin/bash
set -euC
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
test "$#" = 1
[[ "$1" =~ ^[0-9a-f]{40}$ ]]
test "$(git rev-parse HEAD)" = "$1"
test -z "$(git status --porcelain)"
task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg617-export-component-v2
test ! -e "$task_base"
mkdir -m 700 "$task_base"
export JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export PATH=$JAVA_HOME/bin:$PATH
date --iso-8601=seconds > "$task_base/started"
git rev-parse HEAD > "$task_base/source"
git ls-files src tools pom.xml | LC_ALL=C sort -u | xargs -r -d '\n' sha256sum > "$task_base/source-files.sha256"
python3 -B - "$task_base" <<'PY'
import hashlib,pathlib,sys
root=pathlib.Path(sys.argv[1]);old=pathlib.Path('src/schubert-nk-bootstrap/target/jacoco.exec')
assert old.is_file() and hashlib.sha256(old.read_bytes()).hexdigest()=='de38b5aae542a5f6d7118a01c903c856740a9c8d718fb9a0940e39133aa6b8e2'
preserved=root/'preexisting-bootstrap.exec';assert not preserved.exists()
old.rename(preserved);assert not old.exists()
PY
task_result=0
(
umask 0027
python3 -B tools/quality/qualified_nullable_check.py &&
./mvnw -o --no-transfer-progress -Dstyle.color=never -Djansi.force=false -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-bootstrap spotless:check test-compile test spotbugs:check jacoco:report jar:jar -Dtest=NativeCoveragePrivateFileTest,NativeCoverageExportTest,ChildStartupContextTest,FixedNativeCoverageCheckpointTest,FixedServiceIdentityTest
) > "$task_base/build.private.log" 2>&1 || task_result=$?
printf '%s\n' "$task_result" > "$task_base/exit"
date --iso-8601=seconds > "$task_base/completed"
sha256sum --check --status "$task_base/source-files.sha256"
test "$(git rev-parse HEAD)" = "$1"
test -z "$(git status --porcelain)"
cp -a src/schubert-nk-bootstrap/target/surefire-reports "$task_base/"
if test "$task_result" = 0; then
  cp src/schubert-nk-bootstrap/target/jacoco.exec "$task_base/bootstrap.exec"
  cp src/schubert-nk-bootstrap/target/schubert-nk-bootstrap-0.1.0-SNAPSHOT.jar "$task_base/"
  cp src/schubert-nk-bootstrap/target/spotbugsXml.xml "$task_base/"
  cp src/schubert-nk-bootstrap/target/site/jacoco/jacoco.xml "$task_base/"
fi
printf 'PG617_COMPONENT actualExit=%s fixedSource=true vmOperations0=true formalAccepted=false\n' "$task_result"
exit "$task_result"
