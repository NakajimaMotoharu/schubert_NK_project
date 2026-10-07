# PG527 依存全terminal固定工具owner回収（SSC214／BUG824・YKT593）

Productiona2/PG495/schema028、SS343/353 SSC214・QA047。design-onlysource9b7941478/PR49→main7711eb13544cbddedf27eccf75a2e7df0f49d366確認。Caddy-Web-API-Cleanup四receipt、Expiry/Broker/Cleanup依存PID1 stop-done、原本SUCCESS/ISSUED7/24-462/Backup/当nativeを保持。旧PG526 Ref例外保持には復帰入口が無いため、元source/未保存後四receipt/UNKNOWNを変更しない。

| Test ID | 独立期待値と根拠 | command |
|---|---|---|
| PG527-H01 | Root561260/Ref561289のPID/ticks/argv/全task子/RootUID、宣言3項+primary開始/終了/PID/code/status、sole当peerのliteral正常・null/欠落/foreign63assert | pg527_terminal_handoff_test.py |
| PG527-H02 | PG502原cold五key/owner/lock9値のliteral73assert。別artifact/schema/null/bool/mode拒否 | pg527_reference_schema_test.py |
| PG527-H03 | exact10 Unitのcurrent固定4generation、4receipt、API-Web所定TERM143/failed、oneshot/RemainAfterExit yesのCleanup-Expiry正常0/元exit履歴保持、Broker1/143success、欠落/foreign全field459assert。journal field順だけ正規JSON mapping等価・raw保存別SHA・重複拒否 | pg527_terminal_matrix_test.py |
| PG527-V01 | 現owner/M-A/peer/immutable6・全10kernel終端、宣言とprimary履歴分離、四receipt/API-Web fulljournal再認証、vendorと当PID1依存3job（Expiry33502→Artemis33499→Cleanup33498）を二読 | same source execute(False) 読取専用preflight |
| PG527-V02 | 新読取十Refで各Unit18履歴を保持しfixed Ref→JavaだけpidfdTERM一回、全現24-462/原本Backup/startup7/native/runtime/旧18fileと全terminal前後二読不変、自owner/peer/advisory/FLOCK0・新Ref/bus正常close。業務stop/start/reload/revoke/DBwrite0 | pg527_terminal_handoff_native_v1.py |

初期preflightは新broker全journalのJSON field出力順によるrawSHA差でguard拒否、操作/SAVE/TERM0（未実装fixtureとして保持、合格へ算入0）。全cursor/全field値/stream順を独立canonical JSON hashで比較し、新captureの**rawbyteは別privateファイル/SHAのまま保持**。既DB/raw artifact/旧SAVEを正規化して書換0、外部画面/電文順序は無関係で変更0。

実行OS Ubuntu VM、bootcc9、Python標準lib＋既dbus、source固定後new-only一回。全private/hashはRoot pg527-prestop-owned-handoff-v1とhostPG379へ、Gitは秘密無し集計。独立595assert/undefined0、Production PT/coverage増分0。旧PG526工具のactual143/UNKNOWNと当限定回収actual0を区別し、別fresh全M-A/DB/十Ref正常終端/readback/native/正式品質は未完。実結果後記。
