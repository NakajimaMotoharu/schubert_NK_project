#!/bin/bash
# BUG897/YKT666 actual production factory with real temp FD and independent golden data.
set -euC
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation
test "$#" = 1
[[ "$1" =~ ^[0-9a-f]{40}$ ]]
test "$(git rev-parse HEAD)" = "$1"
test -z "$(git status --porcelain)"
task_base=/home/mini/codex/project1/work/pgpt-runs/PG379/pg628-retention-factory-component-v1
test ! -e "$task_base"
mkdir -m 700 "$task_base"
export JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export PATH=$JAVA_HOME/bin:$PATH
date --iso-8601=seconds > "$task_base/started"
git rev-parse HEAD > "$task_base/source"
git ls-files src tools pom.xml | LC_ALL=C sort -u | xargs -r -d '\n' sha256sum > "$task_base/source-files.sha256"
python3 -B - "$task_base" <<'PY'
import pathlib,sys,hashlib,json
root=pathlib.Path(sys.argv[1]);target=pathlib.Path('src/schubert-nk-batch/target');old=target/'jacoco.exec'
assert old.is_file()and(target/'surefire-reports').is_dir()
digest=hashlib.sha256(old.read_bytes()).hexdigest();old.rename(root/'preexisting-batch.exec')
(target/'surefire-reports').rename(root/'preexisting-surefire-reports')
with(root/'preexisting.safe.json').open('x')as f:json.dump({'previousExecSha256':digest,'oldResultsAcceptedHere':False},f)
assert not old.exists()and not(target/'surefire-reports').exists()
PY
task_result=0
(
umask 0027
python3 -B tools/quality/qualified_nullable_check.py &&
./mvnw -o --no-transfer-progress -Dstyle.color=never -Djansi.force=false -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-batch spotless:check test-compile test spotbugs:check jacoco:report jar:jar -Dtest=MorningBackupRetentionTest,BackupArtifactVerifierTest,BackupManifestReaderTest
) > "$task_base/build.private.log" 2>&1 || task_result=$?
printf '%s\n' "$task_result" > "$task_base/exit"
date --iso-8601=seconds > "$task_base/completed"
sha256sum --check --status "$task_base/source-files.sha256"
test "$(git rev-parse HEAD)" = "$1"
test -z "$(git status --porcelain)"
cp -a src/schubert-nk-batch/target/surefire-reports "$task_base/"
if test "$task_result" = 0; then
 cp src/schubert-nk-batch/target/jacoco.exec "$task_base/batch.exec"
 cp src/schubert-nk-batch/target/schubert-nk-batch-0.1.0-SNAPSHOT.jar "$task_base/"
 cp src/schubert-nk-batch/target/spotbugsXml.xml "$task_base/"
 cp src/schubert-nk-batch/target/site/jacoco/jacoco.xml "$task_base/"
fi
printf 'PG628_COMPONENT actualExit=%s fixedSource=true nativeAcceptance0=true formalAccepted=false\n' "$task_result"
exit "$task_result"
