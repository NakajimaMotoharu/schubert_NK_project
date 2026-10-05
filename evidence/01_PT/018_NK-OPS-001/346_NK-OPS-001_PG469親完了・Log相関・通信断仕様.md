# NK-OPS-001 / PG469 親完了・Log相関・通信断（暫定）

関連RD OPS009/MON003/TST004、UI251/252、SS341/342/343/324§9/351/355、SSC190/191、BUG742/749/750・YKT523/527/530。Production source `d3bba6db6eb9fec13e4847a10541cf337f575731`、PG469署名digest `cc5e4dd7ca70d3a21e1145dd35b9f047856c4ab83bfac6f11722663ba7744462`。正式run24や旧BBBの結果を流用しない。

| Test ID | program/class/method・入力/操作 | 独立期待値・事前条件 |
|---|---|---|
| PT-OPS-P469DONE001 | MorningProcessMain実親のPID1 journal / Pg469CompletedReadback.jobDone,parentAfter | boot e07aa706、Invocation aabcc2c3…、start job162935、PID1/UID0/systemdの正規doneが元30分以内に1件。GC零値単独は合格根拠にしない。固定フィールド・null/欠落/型/別世代/時刻境界の独立374assertを実行 |
| PT-OPS-P469DONE002 | 同新読取M/A/DB advisory / StartupPermitFiles・MaintenanceRunFiles・固定SQL | ISSUED/new activation、DONE SUCCESS、namespace45/intent0、旧40の全byte/metadata不変。旧351×14全値不変＋同runの再開10step各SKIPPED/count0（既存成功の再実行防止）。Backup全20entry不変、原本の旧regular file（active差替えを除く）保持、19業務table不変。全新scope通常返却を終了code0後に認定 |
| PT-OPS-P469DONE003 | parent.exec / pg469_parent_native_probe.py | append=falseの今回単一session・開始/終了timestampが同親window内、同frozen6projectJAR NoMatch0、Morning正常帰還540/542実到達。47/543のpartialを100%へ補正しない |
| PT-OPS-P469CHR001 | shared Current CHR-A01 / pg469_capture_a01_when_ready.py | 独立Current baseline＋承認DIF001/QA045の名称差分のみ。別sourceや未実行caseを全gateへ合算しない |
| PT-OPS-P469LOG001 | NativeNkL01Capture469・shared Current L01 / retained accountによるLogin→検索→Log表示 | SS351 LOGIN_SUCCEEDED/SECURITY・SCENARIO_SEARCHED/ACTION各1、HTTP完了REQUEST。password reset0、資格情報600・raw出力private。UI/SS355の比較改訂QA051は未回答なのでOBSERVED_NOT_ACCEPTED。watermarkだけで相関としない、VIEWED操作はこのdriverでは未実行 |
| PT-OPS-P469LOG002 | pg469_log_readback.events,compare / 同Web世代journalと読取SQL | local event IDとDB source_message_idの集合完全一致・各投影field/timestamp/count一致・欠落重複0、固定17negative（欠落、重複、別PID/INV/時間窓、不正field）。raw journal/DBはprivate600、Gitへhashと集計だけ |
| PT-OPS-P469LOG003 | pg469_log_network_outage / 独立102assert→隔離VM実通信拒否→5GET login→復旧 | 初期nft空、same4peer/current署名source、uid997→IPv4loopback61616だけ新tableでreject。5HTTP200/5local event、実packet counter>0、5outbox ERROR/attempt>=1/DB0を拒否中に確認。finallyで当tableのみ削除し原ruleset復元、復旧後同5event SENT/DB各1・peer同一。Broker process停止・API停止の試験とは区別する。raw cookie/電文/rowは保存公開しない |

## 実行・証跡・範囲

Host JDK25.0.4 / guest Ubuntu26.04, JDK25.0.4, PostgreSQL18.6。`bash tools/quality/vm/050_s1/pg469_readback_compile_v1.sh`（374独立/Werror0）→new-only Root400 stage→`pg469_readback_native_v1.sh`。`python3 -B .../pg469_parent_native_probe.py`、`bash .../pg469_l01_native_v1.sh`、`python3 -B .../pg469_log_readback.py --selftest|--native-v1`。通信断はnew-only Root私有工具をexact byte照合して一回だけ実行する。失敗時もnftの原状態復元を照合し、再実行は別run/再認証を要する。Root予約/結果は `/var/lib/pgpt-s1-preservation/pg469-log-network-outage-v1`。

安全集計manifestは `evidence/provisional/PG469-parent-log-native-v1/manifest.json`、rawはWorkPG379/Root保存物。実行日時・終了code・source・hashは結果347/manifest。正式coverageは未達、Java/JSの要求100%・NPE/negative・静的gateは不変更。この工具独立assertをProductionPTへ加算せず、full3301/489/FES0/static6zeroはD3の既存fresh結果を対応付ける。IT/ST完了は宣言しない。
