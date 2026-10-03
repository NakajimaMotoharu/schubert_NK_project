#!/bin/bash
set -u
umask 077
cd /home/mini/codex/project1/work/pgpt-foundation || exit 2
test "$(git rev-parse HEAD)" = 78d485c47bf951bffb9a56804b80358779cc7256 || exit 2
git diff --exit-code HEAD -- src tools pom.xml || exit 2
test -z "$(git ls-files --others --exclude-standard -- src tools)" || exit 2
test ! -e /home/mini/codex/project1/work/pgpt-runs/PG379/pg446-six-full-v3.log || exit 2
export JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4
export PATH=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin:$JAVA_HOME/bin:$PATH
test -x "$JAVA_HOME/bin/java" && test -x "$JAVA_HOME/bin/javac" || exit 2
test -x /home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node || exit 2
test "$(/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --version)" = v24.19.0 || exit 2
"$JAVA_HOME/bin/java" --version > /home/mini/codex/project1/work/pgpt-runs/PG379/pg446-six-full-v3.preflight.log 2>&1
"$JAVA_HOME/bin/javac" -version >> /home/mini/codex/project1/work/pgpt-runs/PG379/pg446-six-full-v3.preflight.log 2>&1
./mvnw -o --version >> /home/mini/codex/project1/work/pgpt-runs/PG379/pg446-six-full-v3.preflight.log 2>&1 || exit 2
date --iso-8601=seconds > /home/mini/codex/project1/work/pgpt-runs/PG379/pg446-six-full-v3.started
git rev-parse HEAD > /home/mini/codex/project1/work/pgpt-runs/PG379/pg446-six-full-v3.source
(
umask 0027
umask > /home/mini/codex/project1/work/pgpt-runs/PG379/pg446-six-full-v3.child-umask
./mvnw -o --no-transfer-progress -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api,src/schubert-nk-web,src/schubert-nk-batch clean spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report jar:jar org.apache.maven.plugins:maven-dependency-plugin:3.9.0:copy-dependencies org.apache.maven.plugins:maven-dependency-plugin:3.9.0:list -DincludeScope=runtime -DoutputFile=target/runtime-dependencies.txt -DappendOutput=false
) > /home/mini/codex/project1/work/pgpt-runs/PG379/pg446-six-full-v3.log 2>&1
task_result=$?
printf '%s\n' "$task_result" > /home/mini/codex/project1/work/pgpt-runs/PG379/pg446-six-full-v3.exit
date --iso-8601=seconds > /home/mini/codex/project1/work/pgpt-runs/PG379/pg446-six-full-v3.completed
printf 'PG446_FULL_V3 actual exit=%s\n' "$task_result"
exit "$task_result"
