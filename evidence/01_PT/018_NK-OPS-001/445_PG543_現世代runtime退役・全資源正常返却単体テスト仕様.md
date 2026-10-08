# PG543 現世代runtime退役・全資源正常返却

検証順更新2026-10-08 10:51JST：source4e868fc3c stage-v2actual0/probe-v2actual1は十Refなしのdependency比較で拒否。safe診断は四AfterのInspector一token欠落だけ（BUG835/YKT604）、単発loaded照会は同時十Refの代用にならない。C005のprobeは厳密基準へ拒否したまま保全・PASS0、C006の新M-A/RODB/十Ref固定verifyで全原値同値と正常返却を実証してからC007へ進む。snapshot/dependency oracleは弱め0、旧probe再発行0。

実試験更新2026-10-08 10:47JST：source03f875237でnew Tools-v1 stage actual0/probe actual1、release配布Unitをeffective Root0644でstrictしたため拒否（BUG834/YKT603）。旧tool配置/failedlog保全、freshM-A/DB/Ref/SAVE/退役/reload/新start0。署名PG495 stage規約のRoot:schubert(986)/0640/単linkとmanifestのpath/size/shaへ是正、独立literal正/誤GID/mode/type/nlink/size/null/extraの4管理test/Werror新compile-v2/Pyflakes0。新Tools-v2/native-v2をnew-onlyで固定、v1操作再発行0、結果後記。C004/C007の実fault matrix未完、純source順序検査だけで故障網羅認定しない。

NK-OPS-001 / RD OPS009・BAK/BKO / UI251 / SS342343353 SSC192198216217・QA047。ProductionはVM a2/PG495/schema028、host候補969/PG540とは別。PT管理工具、Production PT加点0。

|Test ID|対象・入力・操作|独立期待値・根拠|
|---|---|---|
|PT-OPS-PG543-C001|closed15 snapshot・十Unit18/config20、missing/extra/alias/null/型|literal閉集合、全kernel空・Id loaded・同saved原値。他Unitを加えない|
|PT-OPS-PG543-C002|全十ExecStart補助history/設定各field変異|退役前全一致。退役後Morning signed base＋native no-resume goldenだけ宣言差、他八全一致、Caddy paired validate/run exact preserved又は両方exact n/a。foreign/片側/任意履歴拒否|
|PT-OPS-PG543-C003|READY/VALIDATED/release重複・早期・readonly|retireはbefore→removed確認→DB閉鎖→release、readonlyだけREADYで正常返却。UNKNOWNを補完しない|
|PT-OPS-PG543-C004|保持entry FD・nameのmetadata/byte、namespace、dirsync境界|saved原runtime3992…643Bとdev/ino/uid/gid/mode/nlink/size/time一致。保持callback内でunlink一回・保持dirsync、one daemon-reload、失敗後restore/retry0|
|PT-OPS-PG543-C005|現VM専用reader read-only probe|sealed PG537 before/after/complete hash、退役済二credential sameinode、全24-462/原本Backup/ISSUED7/native9/十F18/設定/依存集合/真正親DONE・PID1 stop履歴不変、peer/advisory0。authorityは付与しない|
|PT-OPS-PG543-C006|別fresh verify M→A→署名187→専用RODB/advisory→十Ref→全原値二読|全新scope正常返却。runtime操作0。Java actualexit0・source/helper/class hash固定、元source/旧143UNKNOWN不変更|
|PT-OPS-PG543-C007|別fresh retire同契約→before・runtime bytes・一回予約durable→保持FD unlink/dirsync→one reload→全後条件→RODB rollback正常close→peer/advisory0→逆Ref/bus/FD正常close→A/M正常→complete|runtimeだけ不存在・Morning同signed/native no-resume宣言。全原値不変・真正既親証拠を保持、新scope全部正常。途中故障はprivate phase保持・隔離維持・completeなし・二重発行なし|
|PT-OPS-PG543-C008|全後条件独立再読・資源後条件|全business kernel/peer/advisory/FLOCK0、PG543 sealed before/after/complete同source、native9/current署名不変。別fresh親/newcandidate/Inspector/全native/正式は未受入|

実行command=`python3 -B tools/quality/vm/050_s1/pg543_retirement_contract_test.py`、`bash tools/quality/vm/050_s1/pg543_retirement_compile_v1.sh`、Pyflakes新工具群。source固定後native工具のstage→probe→verify→retireを各一回（成否確認前次操作0）。new-only失敗記録を再使用0。guest current boot/owner/currentBOMは各操作前再認証。OS/JDKとcommand/actualexit/source/tools/loghashはprivate safe＋sanitized manifestへ保存、raw原本/credential/permitGit0。

着手前群=N15.04既0.83/2/4.17pp、初期269.8pp未較正を消さない。限定ultra read-onlyレビュー1名・新agent連鎖0、数値usage不提供はN/Tnull・共有枠PGPT/PMO専有配賦0。BUG833/YKT602、PG542BUG831832は別失敗と正常readonly再試験を保持。現在管理3test・Werror compile0/Pyflakes0、実stage/probe/verify/retire/C008未実行、coverage/native正式未完。
