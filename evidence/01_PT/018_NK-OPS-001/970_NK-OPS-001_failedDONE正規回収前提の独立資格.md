# 970 NK-OPS-001 failed-DONE回収前提・独立資格

2026-10-16、Source7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e/PG3976/BOM0a409301、RD OPS009/SYS004、UI251、SS343/353/SSC286、修正前SSC287、BUG1332/YKT1098、451/487。これはreadonly/data-onlyの限定証拠で、停止許可・親正常完了・Production PTの新規合格ではない。

## Test ID・独立期待値

PT-OPS-FAILED-DONE-4074-001～004：固定独立NKDONE1六行/最終LF、親13属性、PID1 Starting/JobFailedのmessage ID/job155272/boot79a/inv8208/start-exit境界をfixtureへ直接記載。Production codec/同じmethodでexpectedを作らない。正常0/10への偽装、別source/BOM/boot/inv/job/PID/UID、重複/欠落/成功done/時刻外/非数値/null・別原本を拒否。4試験成功。正例でもparentNormal/genuineRootDone/genuinePid1StartDone/normalUnit0or10/recoveryAuthorityIssued/stopAuthority/formalAcceptedは全false。

PT-OPS-ACTOR-4078-001～002：公開固定uid999/gid981/groups980,981,982,986の独立vector。UID/GID四欄、固定group完全一致・重複/追加/不足/leading-zero、全capability0/NNP1、null/未知値を検査。2試験成功、nullをAttributeError等の正常拒否として算入せず固定ValueErrorで拒否する。以上は工具検査6件でProduction PT追加0。

## 実物との接続結果

4070実0：同署名187/Root8208/timeout143をfresh二読。elapsed1800.068969秒、retained Unit CPUUsageNSec889653578000、MemoryPeak301215744。IOAccounting=no、IO bytes等の`[not set]`は未取得であり0へ変換しない。CPU時間は当Unit/cgroupの累積で、特定method/実行待ちや単独profileの同条件性を立証しない。

4072実0：元PID1 journalをprivate保持（rawSHA4b930e614069ccaee34382ba14d84efaf1274dafd262749c5a77d61accb10f38）。同boot/UNIT/invの6metadata、job155272 start時128735402355→JOB_RESULT=failed/130535471617。MESSAGE本文は公開しない。4076実0：当保存journalの全hash/duplicate拒否と現Root13属性・原本を二読、独立4074へ接続、旧RootPIDと全cgroup空を確認。contractSHA1afbe7f067cf4ee9a1d7431bf38cdeb28bd7ac62ed6ac29f9178d1d7cfa882ae。**原本WARNING10あり・実親143**を分類し、全normal/authority flag falseを維持。

4080実0（07:27:54Z）：全ten状態/全32設定・宣言、187署名/Unitfile、全24表・原本Backup/credential/旧proof/native不変。普通4actorの全UID/GID/groups/caps/NNP/cgroup/子0をfresh NSSへ照合、全FD集合を二回安定確認（API144/Web158/Caddy7/Artemis173）。管理advisory/flock0、普通DB3、native50exec。私有全snapshot SHAfd1177d10f2713596a32de536a3c71d592563cc3b6decb7194bc6c68ea6c21d8。startup33entry/permit8/owner8/launch16/epoch.current、permit-start.intent=false/service intent0。不存在intentを生成/退役しない。

実起動start monotonicはCleanup128779540335→Artemis129039325843→Expiry129170482184→API130044470226→Web130058178055→Caddy130090505390。従って必要回収候補は逆順Caddy→Web→API→Expiry→Artemis→Cleanup。Backupは当cohort正常inactive0、Inspector/Adminは未実行inactiveであり、成功済みstop/不要stopを再発行しない。これはhistorical read-inputであり、操作直前のfresh所有・同世代・全proofを代替しない。

## 実行・証跡・未受入

command=`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/<pg4070/4072/4074_test/4076/4078_test/4080の各実file>.py`。各元実行はnew-only、再演禁止。全tool pyflakes0、guest既存boot79a/current署名を都度検査。公開 `evidence/provisional/PG4082-failed-done-context-v1/manifest.json` SHAe8743e6c442d22517d3c647f0399cad0ee099e0940d9e97bde24135ca5640561。生journal/FD map/DB/credentialはprivateのみ、raw auth session/cookie/token/鍵をGitへ輸出しない。

4068固定manager/Caddy本人/socket primitiveも実0、969の原本whole457msと合わせて単独測定の切分け材料とする。ただし実Root稼働中の負荷・native採取・合成guard反復/DB/HTTP-TLSと同条件ではなく、これだけで当Rootの主因を確定しない。BUG1332原因対策は未完。

SSC287は修正前起票済み・設計draft。fresh新M/A/専用RODB/同peer・十Ref/全原値/全署名・各所定真正terminal/vendor・一回予約/独立post・全scope正常まで実回収許可は未発行、信号/stop/revoke/reload/Root再start0。normal4042やSSC266旧profileを仮構成して使用しない。正式1964PT/53scope・旧個別17/190・工数null・QA051 final保留・F03未受入は不変更。
