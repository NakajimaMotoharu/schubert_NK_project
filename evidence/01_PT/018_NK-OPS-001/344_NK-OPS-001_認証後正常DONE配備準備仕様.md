# NK-OPS-001 認証後正常DONE配備準備

対象：Pg469CurrentReadback/main・allowedChanges/authenticatedFixture、Pg469CompletedDeployment/verify・normalDone/names/stopOwned、pg469_owned_stop/stop_one/broker_witness。RD運用保全・AUT、UI226/251、SS321/341/342/343、SSC190191、QA047、BUG744～748/YKT525～529。管理工具の独立assertionをProduction PT件数へ加算しない。

| Test ID | 事前条件・入力・操作 | 独立期待値・根拠 |
|---|---|---|
| PT-OPS-CURRENT469001 | 現BBB正規DONE、351全履歴/旧341全14列、全Backup、41startup/旧36、User1/version1/auth3、bootstrap退役2。M/A/readonly DB/advisory取得で読取 | 保存済みPG468原値/実PID1 jobdone、認証3回/変更+1・revoke1、DB/秘密不変更、全新scope通常返却後のみ0。期限超過contextは勝手に削除しない |
| PT-OPS-CURRENT469002 | handwritten 23表集合、null/欠落/未知、正常DONEの境界時刻/異run、phase/fatal/suppressed | 承認Loginのapp_users/auth_sessions/login_ip_attemptsだけ認証変更を追加。無関連表は拒否。private原値をexpectedとして読取、Production methodで生成しない。close未知は正常0なし |
| PT-OPS-CURRENT469003 | D3 fresh3301/full/frozen6、新186artifact/187checksum/27SQL/28history、正規ED25519署名。unused Root配置→同M/A現peer/INFO5/socket/TLS→候補RO/verify | 独立hash全byte・公開pin、old current/全設定・既設bootstrap Unit不変。stop/start/DDL/permit0、通常返却。V1拒否/inner-class stage失敗を保全して新限定verifyと区別 |
| PT-OPS-CURRENT469004 | handwritten full18/全journal・Broker各null/欠落/foreign/error/重複/mono境界、明示停止/依存停止全phase故障 | API/Web143はcleanup→stoppedの同INV/boot/PID/UID全journal、Unit成功0への変換禁止。Broker143はinactive/dead/vendor正常stop1。依存停止には二重stop0、各後条件後receipt。独立137→221、TERM240；実停止は未実行 |

実行command：`pg469_current_compile_v3.sh`/`pg469_current_native_v3.sh`、`pg469_stage_candidate_v1.py`、`pg469_completed_compile_v3.sh`/`pg469_stage_completed_v2.sh`/`pg469_completed_verify_v2.sh`、`pg469_owned_stop_test.py`/`pg466_term_witness_test.py`。Host/guest Java25.0.4・PG18.6・Maven3.9.12。限定実source BBB、新candidate D3、工具working hash/HEAD/run/時刻/終了code/private log hashはmanifest。正式Production coverage、全source D3 native、unknown所有故障の実注入、activate/親新source/全CHRは別受入でnot-runを合格にしない。
