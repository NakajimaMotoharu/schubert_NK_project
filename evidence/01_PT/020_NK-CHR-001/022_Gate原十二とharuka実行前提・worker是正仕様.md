# GateCli 原whole12とharuka実行前提：source・所有・資源の閉鎖

NK-CHR-001/WBS-P02001/F03/F04、TST004/SS355/451。原GateCliTest全12method（745行）はfixture/原Current公開reportsとcatalogだけを対象。実Currentの起動/採取・原本DB/master/Root/cohort/native/role/配備/VM操作をしない。preflightは自己所有fakefile/permission/realFileStore容量・URLregex/port整数だけでDB/Network clientやfake executable実行なし。baselinePromotionは新TempDirだけ、正本Currentbaselineはread-only。資格情報はsynthetic canaryで実authではなく、raw private logsは公開しない。

前提の二filesystem: SOURCE_ROOT/target/preflight-testは実空き20GiB以上、Junit TempDirは実空き20GiB未満の低容量FS。空き値をmock/期待値変更で合わせず、harukaのfresh disk/tmpfs値から決定する。必要RAM/Java/Maven/surefire設定も既POMと照合。hostはserver.info haruka専用接続/PMO knownHosts pinのみ、oldaru driver/VM/keys/permit/run成功を流用しない。接続前にoperation/source/ownerを凍結、readonly id/hostname/boot/proc-self/resource/tool metadata確認まで。新test/source snapshot/job startは本群では禁止、aru新規操作/停止再起動/初期化0、haruka業務schema/role/サービス/Root/native/HOLD解除0。

BUG2873: 原AtomicJsonの正常/例外でfinally release latch/countDown→shutdownNow→await10 assert、helper await5/Future5・第二writer拒否/初writer完成/part消去/null拒否と他11methodを一切変えない。動的hang probe0、source inverse/独立oracleを先行し、test実行は別群。元原12に新JUnit追加0。

GateMain667行・Test745行・POM/Maven args・全case/helperのreachable副作用を確認。既ArtifactComparator/GateValidator/TargetAdapter/Correlated46のsource/証跡は適用性参照、確認だけで再実行せず、未実行Gate12＋修正を含む必要common全58のsingle-source通常/static/coverageは前提成立時に別見積り。実業務CHR/NK受入や正式1964/53とは分離する。

本群.45/1.35/2.7 cap3: SOURCE_REQUALIFICATION source入力/副作用.2/.6/1.2＋haruka readonly pin/所有/資源.15/.45/.9、REWORK worker.1/.3/.6。事前のlocal公開Test候補読取は予備判定で、token/専有費は欠測null・本群成果へ二重加算0。host準備はPMO担当分をPGPTへ配賦せず、追加実行/normal価格は前提確認後に別凍結。元費用/原S/V上限/群開始見積りを保存する。
