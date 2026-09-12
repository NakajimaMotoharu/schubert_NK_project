# NK-OPS-001 run環境publisher実行結果

正式確定: PT-WEB-20260912-04/sourcee8bb5731c57bd5c03526202fc51c9009ffe3e2b5、2026-09-12 22:15:42～22:23:07 JST、終了0、全1145件（Storage58/Batch91を含む）、6 Java moduleの4coverage100%・Production静的解析PASS。PUB001～012はOPSへ一意所属、OPS全78件、18負canary/12collector/35scope同run/source/hash照合成功。BUG151～153/YKT117～119は各audit対象の再試験・修正/非該当根拠を完了。manifest.jsonとchecksums.sha256を正とし、以下は探索履歴。親OS/固定namespace/子制御/backup/原本を認定したものではない。

017/PT-OPS-PUB-001～012、PG-D-154。探索4は2026-09-12 22:12:09 JSTにStorage58/Batch91＝149 PT成功、4coverage100%・NullAway/Spotless/SpotBugs PASS。source固定の正式全reactor/証跡照合はこれからであり、正式03へ遡及算入しない。親固定namespace/OS lock/子終端/永続run原本は別必須残件。

実行command: JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-batch -am verify。終了code0。raw log SHA256 f2f1adccffaef0b809c9de4781bf0ff740f9e3fc85d10ef741f7e88e51c8eba9。Publisher3class/30method/121line/40branch、共有Policy3class/10method/51line/82branch、Reader2class/18method/67line/34branchはいずれもmissed0（interfaceの実行体なしは無除外）。17＋1＝18負canary成功。関連BUG151/152/153・YKT117/118/119は正式run後に完了認定する。evidence/logsの各番号に失敗runと再試験根拠を保存。
