# NK-OPS-001：Completion非再入・PG461 timeout隔離

Program/class/method: MorningStartupLaunchOwner.publishCompleted、MorningCompletionChecks.verify/ownerGuard、MorningCompletionEvidence.verify。RD OPS009/BAK001、UI251、SS341/342/343/355、SSC185、QA047、BUG693/YKT497。親30分/旧失敗/同DB/元原本を保持し、別DB・guard省略・normalization・旧/run復元をしない。

| Test ID | fixture/操作 | 独立期待値・根拠 |
|---|---|---|
| PT-OPS-TXOWNER001 | TX状態booleanをfalse、旧複合guardと新ownerを呼ぶ | 旧guardは独立DB非再入ルールで拒否、新ownerはpeerだけ・TX falseのまま・DB読取0。TX外はpeer→DB→peer |
| PT-OPS-TXOWNER002 | new/reused/failed evidence、4種DB再読で同TX内owner前後 | 各owner値83ns、TX変更0、4再読/peer14回。旧callbackなら最初のTXで拒否。正常/Backup失敗ともSS341の後条件維持 |
| PT-OPS-TXOWNER003 | peer前/後、DB、budgetに独立IO fault | 同じ例外伝播・以後の未実行・期限再発行0。DB failure後peerを実行成功へ加算0 |
| PT-OPS-TXOWNER004 | null peer/DB/budget | constructor/factory境界で拒否、NPE catch正常化0 |
| PT-OPS-OBS462001～004 | 固定ordinary status、Root移行503、200UP/info不一致、全authority両側/null | ready前移行を未認定継続、真正ready時だけ両actor固定権限。Root外部capture欠落の偽補完0 |
| PT-OPS-ISO462001～003 | 独立18-field parent timeout143/live普通peer/旧16+当7 namespace/全caps | foreign/known30/null/不正値拒否、固定23名、操作権限は新operatorのM/A/DB。実機verify後だけ逆順stop/全9終端、301行/原本/Backup/全startup不変 |
| PT-OPS-RET462001～003 | 独立NKLAUNCH1 byte、shell sha256sum固定vector、21post名 | 異世代/offset値/ownerhash/role/null拒否。実全終端→ISSUEDを同permit由来INVALIDへcanonical revoke→publication-first quarantine→typed三intent退役。旧143/旧close不明は不変、原本pending/旧16+当4/301/Backup不変 |
| CHR-A01（同00785 source） | Current共通browser/実CaddyCA600/login | Current baseline全field完全一致、DIF001/QA045 titleだけschubert NK - ログイン。CSP/CSRF/headerを正規化しない。全gate/L01/親成功は別未受入 |

実行command: `bash tools/quality/vm/050_s1/pg462_txowner_selected_v3.sh`（61PT/9suite、explicit全6の依存controlも実行）。`python3 tools/quality/vm/050_s1/pg462_observer_identity_test.py`。外部工具はJDK25.0.4 `javac -Werror -Xlint:all` と独立Test main、frozen00785 six classes/runtime jars/closedbaseを明示。VM operatorは新root0500/0400 namespaceをhash閉鎖し、verify/isolate/retireを別command・new-only private logへ保存。生存既知値は実行前後に再照会する。

実PG461 failure/private stack/heap/timeout143/旧watchfailureはWorkPG379にimmutable保存。heap/DBdump/原本/token/credentialはGitへコピーしない。正式source/run/全scope100は未成立、selected append execを全coverageとしない。新linear helperはclass/method/line missed0、BRANCH命令なし0/0の実XML根拠を記録。全体回帰は同所有変更群source固定してfresh全6/NullAway/静的/JUnit/JaCoCo/前後hash/終了を照合後にだけ受入する。OS/JDK/Maven/Node/command/time/hashは335とmanifest参照。
