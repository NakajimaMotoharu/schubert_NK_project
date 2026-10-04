# NK-OPS-001：Caddy親期限・当known30復旧

対象：MorningStartupLaunchOwner.publishCompleted/caddyRemainingFloor、BackupUnitStartClient.createCaddy/caddyAdmissionFence、MorningCaddyReadiness、当世代Pg463 operator。RD OPS009/BAK001、UI251、SS341/342/343/355、SSC186、QA047、BUG697～701/YKT501～504。既存親30分・同M/A/DB/原本・同peer/startup契約を変更しない。設計正本はmain c28fb505e27ef65bd3cb76dc4bce14b55c9b658b（設計only PR17）。

| Test ID | 目的・事前条件・入力/操作 | 独立期待値・根拠 |
|---|---|---|
| PT-OPS-CADDYFENCE001 | 実Started API/Webを固定fixtureで保持しcompound admissionを呼ぶ | literal12event列full→API-context/owner/marker/owner/context→WEB同5event→full。full2、owner4、synthetic初回start2のみ、同intentの退役後は拒否。各full内peer→DB→peerは既存独立MorningCompletionChecksTestで確認 |
| PT-OPS-CADDYFENCE002 | 12event各pointでIO/Runtime/Error | 同primary identity、期待prefixだけ実行、後続証拠を合格化しない。注入位置の到達を確認 |
| PT-OPS-CADDYFENCE003 | full/owner/API/Web null、逆role、close-only child | factory境界で拒否、NPEをcatch正常化しない、別世代/所有を代用しない |
| PT-OPS-CADDYFENCE004 | parent remaining100s/18s/30s/30s+1ns/30min、0/負/上限超 | 独立算術max(0,remaining−30s)、100s→70s、29.999999999s経過pass・exact30s拒否。元preflight起点から一度固定、Linux/System.nanoTime origin混在/loop更新なし。parent earlier deadline維持 |
| PT-OPS-KNOWN463001 | 実PG462 immutable observerと11変異/両ready欠落 | actualsource ca332/parent4105/API2dcf/Webe5b/PID/ticks/closed9identity/caps/info5/socket相関を要求、14独立assert。期待値をproductionで生成しない |
| PT-OPS-KNOWN463002 | literal18field終端、NKLAUNCH1独立byte、旧20＋当4＋epoch.current、全phase/欠落/foreign/逆戻り/UNKNOWN close | 親30・API/Web143のみ、typed WEB→API→publicationの3段退役、最終25。350独立assert、全旧記録各欠落拒否、unknown時M/A又はMを保持し旧失敗を正常化しない |
| PT-OPS-KNOWN463003 | 同e07boot/currentbcd85、私有14captureSet/fullBOM027、全311/full14/business/fixture/原本/Backup | 新operator M→A→DB/advisory取得、固定enum reverse isolation→全9kernel空。verify変異0→canonical quarantine/typed三退役→原本pending/DB等不変/最終25/outer正常帰還。旧tool/親normal0or10の主張0 |
| PT-OPS-CODE463001 | code-only literal25集合/全欠落/foreign intent/args/null/固定旧新source/release | 独立68assert/Werror0、OLDca332/PG462/digest421、NEXTPG463、311保存。新候補signature/frozen byte/current同世代を実配備前後に照合。DDL/start/permit0 |
| PT-OPS-COHORT463001 | actualmanifest/watchhashと全新工具literal/oneStart/loaded/25/budget1800 | opaque sourceを行数置換で変えない、compile-only annotationsを明示しWerror保持。oldcohort/不存在Unit/余剰namespace拒否 |
| CHR-A01 PG462 | 共通Current driver、同ca332真正Caddy TLS200 | 全Current固定oracle一致、承認DIF001/QA045 titleだけ変更。親normal30/全gate/新source成功へ合算しない |

実行command：`bash tools/quality/vm/050_s1/pg463_caddy_selected_v1.sh`（explicit14suite/全6依存controls）；`python3 -B tools/quality/vm/050_s1/collect_pg463_caddy.py`。native工具は`bash tools/quality/vm/050_s1/pg463_known30_tools_v2.sh`、`pg463_code_tools_v1.sh`、`python3 -B .../pg463_check_cohort_bindings.py`。VMは新root閉鎖class3と固定PG462 release/runtime/baseからPg463OwnedIsolation、Pg463Known30PairRecovery verify、同mainを別commandで実行。操作前のPID/Invocation/currentを再同定し歴史値からstop/startしない。

全回帰trigger=SSC186/BUG697の同所有・期限変更群の機能受入。source/試験/tools固定後`bash tools/quality/vm/050_s1/pg463_full_v1.sh <git実HEAD40hex>`をfresh全6完走しactualexit/XML/source前後hash/静的/NullAway/全byteを照合、同source署名候補から新外部親一回・-B observer先行・同Caddy/原本DONE/intent/outerへ実接続する。全体coverage100/正式source-run-scopeは別gateで、append選択JaCoCoや別ca332 nativeを新sourceの合格へ加算しない。

OS/JDK/tool/time/source/coverage/実結果/証跡hashは337/各manifestへ一意参照。private watch/dump/原本/heap/credential/tokenはGit/通常logへコピーしない。scope外L01 QA051のoracle変更は承認待ち、既存Current baseline不変更。
