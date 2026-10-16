# 971 NK-OPS-001 failed-DONE回収工具：独立仕様・結果

2026-10-16、Production7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e/PG3976/BOM0a409301。RD OPS009/SYS004/TST004、UI251、SS343/353/354、SSC286/287、451/487、BUG1336～1339/YKT1102～1105。当資料は工具・readonly資格であり、Production PTや親正常完了への新加算は0。

## Program/class/methodとTest ID

| 対象 | Test ID / 独立期待値・観点 | 結果 |
|---|---|---|
| 4086 Plan.reserve/terminal/revoke/finish、4102 Recovery.one/complete | PT-OPS-RECOVERY-PLAN4086/PROTO4102：実起動順から逆順6を手記。各verify→耐久予約→verify→一回stop→terminal→verify→recordの7境界、全42失敗prefix、重複/飛越/早期revoke/null/未知/偽terminal拒否。失敗時再送0 | 純試験合格 |
| 4086 invalid_epoch / 凍結recovery_plan | PT-OPS-RECOVERY-EPOCH4086：SS343 SSC089/PG302のNKEPOCH1固定9行、**cutoff_utc**、最終LF、固定boot/run/cutoff/activation・非zero epoch。期待列は同methodで作らずliteral。state INVALID/digest -以外不変、旧cutoff key/CRLF/欠落/順序/異run拒否 | 是正後純試験＋4124実consumer合格 |
| 4090/4094/4098素材検査 | PT-OPS-RECOVERY-METADATA4094：9属性(dev/ino/uid/gid/mode/nlink/size/mtime/ctime)+byte/hash/ACL。atimeだけ許容、他各属性・byte・ACL差拒否 | 純3・4094/4100実inspect0 |
| RootFailedDoneRecovery.frame、4096 exact FRAME fixture | PT-OPS-RECOVERY-FRAME4096：verbatim subject・独立CONTINUE/LF、malformed/32byte超過/null/partial+pulse喪失/entry interrupt/pulse内interrupt/ACK読取時interrupt。正常以外で次phaseへ前進しない | before失敗1保持、after6/拡張8観点0、JDK25 lint/Werror0 |
| 4104 emitted snapshot/peer/holder/stop、4106/4124 freeze/inspect | PT-OPS-RECOVERY-DISPATCH4104：最終全closure静的、実FD new-only reservation、全値/二snapshot/同DBpeer identity（heartbeatによるstate遷移はidentityでない）、外国argv/終了child/現在capture差拒否、一固定stop/120秒・旧Root正常化0 | host合格・4124実inspect0。recoverは未発行 |
| 4122 destination/preserved | PT-OPS-RECOVERY-NATIVE4122：SS/SSC193194の固定agent output=none/append=false/dumponexit=false、ordinary API/Web・同INV、固定2 directory/terminal name。既native不変、停止済みroleだけnew-only file、固定UID/GID/0600/link1/header/hash/全namespace/親inode。未知option/別role/INV/既存・余剰・欠落・旧file改変/ACL差拒否 | 純3＋4124実事前条件合格。実native terminal/CRC資格は未完 |

共有4074 failed-DONE分類4、4078 ordinary authority2、4084 typed inspection2及び継承guard試験も同群で実行。PG4128の**host工具33試験成功・Failed/Error/Skip0、host全工具＋最終emitted Python静的0**。実FDは隔離temp directoryのみ、Unit/DB/VMへのfixture操作0。Java8観点は別の実FRAME試験であり33へ算術加算せず、Production全3717PTへも加算しない。工具のline/method/class/branch100を主張せず、正式Production四100は依然未達。

## 実行と固定成果

command：`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg4128_recovery_abi_and_evidence.py`。対象branch dev-foundation、基点HEAD17ea0018c、実tool全source hashはmanifestに固定。JDK25.0.4/Javac lint+Werror、Python3、Linux。実時刻は各manifest UTC。全体回帰/既成功署名/VM startは反復0。

4088旧Java BD9298と4094 positiveを保全。BUG1337修正後4098 compiler actual0、JavaSHA698e309ca8c479d89387f9ff9bae6bf7276d0146904af523b532f5bd03b74744・全2class固定、4100実readonly inspect0。BUG1338はplan素材だけ変化し、4112で旧6素材をhash/9metadata/ACL検証後、**同Java/annotation/2classをbyte同一コピー・javac再発行0**。新planSHAa990844241e0e3c2c140151cea7f406e423c5b62a30f3bcbb8bc962fa77613d1。

4106旧oracleはcutoffで拒否1、4116旧observerはvendor destfileで拒否1、補助4120もdestfile欠落の読取拒否1。全てJava/M-A/DB取得前で、stop/revoke0。旧失敗を上書きせずBUG1338/1339へ追跡。SS/Productionを工具都合で変更していない。

**最終4124元exec94548 actual0**、08:41:32Z。frozen dispatchSHA73f0c21339fc224dea4d0ebcf14096cf44339b2f48c59c64839a44d6a063d084、78578byte。現aru/QEMU4599/t101242・forward20445/t104194・guest79a/source7bb/BOMをfresh認証。実M→A、batchRO/71419602、普通API2/Web1と本人DBの両端socket、十metadata Ref、全187署名/32設定/24表/原本Backup/鍵/native50/全33 startupを検証。expired Rootはdata-onlyのまま、typed ISSUED/permit/owner/launch/.done10をread-only確認し、新DB/M-A/全Ref正常返却。旧Root143不変、停止/revoke/Root/Backup/Admin/配備/reload/DB更新0。

公開 `evidence/provisional/PG4128-failed-done-recovery-qualification-v1/manifest.json` SHA **e9a80e79acbefa74d45daf94f9fa5c71a3b5bf49543cfd71b7e3ca7b9a76a93e**、全15元manifest/hashとhost ABIログを対応付ける。生DB/FD/journal MESSAGE/argv/session/credential/keyはprivateのみ。native headerはstream/source/CRCの全資格の代用でない。

## 残り・受入境界

SSC287限定設計を確定/main公開し、同artifactのrecover一回と別fresh独立postを接続してから操作する。必要な6 Unit以外のstopを発行しない。未知終端/closeは保持、旧Root143・旧close不明を正常へ変換しない。BUG1339/YKT1105の実停止/native終端後条件は未再試験。BUG1332原因対策・正常親/Browser/新native資格/四100/F03/451/CHR/trace/引継ぎは別未完。正式1964PT/53scope、既17/190は履歴、工数null、QA051 final保留を維持する。
