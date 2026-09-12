# NK-OPS-001 run環境publisher実行結果

017/PT-OPS-PUB-001～012、PG-D-154。探索4は2026-09-12 22:12:09 JSTにStorage58/Batch91＝149 PT成功、4coverage100%・NullAway/Spotless/SpotBugs PASS。source固定の正式全reactor/証跡照合はこれからであり、正式03へ遡及算入しない。親固定namespace/OS lock/子終端/永続run原本は別必須残件。

実行command: JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-batch -am verify。終了code0。raw log SHA256 f2f1adccffaef0b809c9de4781bf0ff740f9e3fc85d10ef741f7e88e51c8eba9。Publisher3class/30method/121line/40branch、共有Policy3class/10method/51line/82branch、Reader2class/18method/67line/34branchはいずれもmissed0（interfaceの実行体なしは無除外）。17＋1＝18負canary成功。関連BUG151/152/153・YKT117/118/119は正式run後に完了認定する。evidence/logsの各番号に失敗runと再試験根拠を保存。
