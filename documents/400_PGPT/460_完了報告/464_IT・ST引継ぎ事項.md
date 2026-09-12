# IT・ST引継ぎ事項

2026-09-13 最新確定: dev-foundation/source a4317d05982a27e74e64b027e2a6b8df56b8c2e5、正式PT-WEB-20260913-01（00:25:37～00:33:14 JST）、全1181件（Protocol80/Storage58/API634/Web241/Batch127/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定/etc・/runの2 method限定静的レビューを記録しcoverage除外なし、CHR runnerのSpotBugsは未設定。12collector/35scopeの同run/source/branch/hashと20負canary成功。DB26部品240＋batch5部品57＋OPS11部品94＝42部分成果391 PT（全1181の内数）。PG157の借用root永続read/publish/remove12件を認定、全IO位置故障/実2instance no-replace競合/実link拒否/保全と4実file byte証跡を確認しBUG158/YKT123完了。R002環境file範囲は確定、固定原本namespace/graph・親実子制御/backup artifact・全cleanup caller・通常Question writer/replay・Logout RERUN001・QA045は残る。PG158の固定namespace/lifecycle24件はSS/PT仕様のみ、未合格。固定加重約4割（35～50%、456）を維持、残件は460。実NK CHR/IT/ST完了とはしない。利用枠残80%でPG/PT継続中、元dev-web3file保全。以下は履歴。

過去記録（正式12、当時の件数比は現在の加重進捗に使用しない）: 最新確定: 正式PT-WEB-20260909-12、source 970681dfb6e2a0ba021c71402cdc5b69fb950b0d、dev-web、2026-09-09 03:27:49～03:32:41 JST。全790件（Protocol80/Storage34/API394/Web241/CHR41）、failed/error/skipped0、5対象moduleのline/method/class/branch全100%、NullAway/Enforcer/format PASS、SpotBugs0。Web165件、Admin73、Inbox11+3+4、Media61、Scenario155/Auth91等は重複する内数。API0102のlocal session破棄/HTTP終端/全result分類8件を追加PASS、DB削除前・commit故障/実HTTP/100並行/新Login非削除を確認、SSC-048完了、7collector収集成功。CHR41はrunner単体試験であり実NK互換gateではない。Logout revoke queue・本番logger固定/残画面/全layout登録/起動/実NK CHR、QA-045承認依存は継続。確定Program5/20=25%（件数比、工数換算なし）、再走待ち1件（RERUN-001/SSC-045、455のLogout期限設計）。PG-D-118のScenario6電文clientとPT166～173を先行仕様化し、画面接続へ継続する。以下は履歴。

過去記録（正式ADM04）: 最新確定: 正式PT-ADM-20260908-04、source 1f1d321ad40bd7ba5f8461e5954e94e7ac6142d3、dev-admin、2026-09-08 15:59:29～16:03:00 JST。全571件（Protocol80/Storage34/API340/Web76/CHR41）、failed/error/skipped0、5対象moduleのline/method/class/branch全100%、NullAway/Enforcer/format PASS、SpotBugs0。Admin23、Media61、Scenario151/Auth91等は重複する内数。User作成/状態/role/password/unlock、実PG監査・全session失効・故障rollback・独立PBKDF2/USRMUT24・並行raceを追加PASS。BUG-045～047/YKT-040～042は再試験完了。正式03は静的解析失敗で非合格。SSC-031の外側Inbox接続とSSC-032の新規canonical接続、HTTP/起動/実NK CHR、QA-045承認依存は継続。確定Program5/20=25%（件数比、工数換算なし）、明確な行き詰まり0件。以下は履歴。

## 1. 位置づけ

後続Linux serverでのみ確定できるcomponent間、実service、性能・容量・可用性・運用の実測値を引き継ぐ。本工程はIT/ST完了を宣言しない。

未実装のProduction/設定artifact/単体異常系をITへ移してPGPT完了にはしない（460）。実NK比較は本工程の残gateであり、CHR41 runner PTや後続deployed試験で代替しない。

## 2. 初期引継ぎ

| ID | 項目 | PG/PTで保証する範囲 | Linux serverでの確認 | 状態 |
|---|---|---|---|---|
| ITS-H-001 | Caddy/Web/API/Artemis/PostgreSQL接続 | 設定schema、単体契約、sanitized fixture | TLS、systemd順序、実socket/credential/権限 | 引継ぎ予定 |
| ITS-H-002 | Artemis容量・再配送 | Embedded/schema、1/5/25秒、DLQ/Expiry契約 | Journal/paging、disk 90%、restart、実時間 | 引継ぎ予定 |
| ITS-H-003 | PostgreSQL backup/restore | DDL/Flyway、role/grant、command contract | `pg_dump -Fc`/restore、RPO/RTO、専用role | 引継ぎ予定 |
| ITS-H-004 | 性能・大容量file/media | Range/hash/atomic file単体境界 | Master 59,627 file/19,240,707,190 byteで容量・性能 | 引継ぎ予定 |
| ITS-H-005 | Characterization | NK adapterと関連case単体契約 | Deployed NKで24 case、DIF-001～016のみ | 引継ぎ予定 |
| ITS-H-006 | Password照合p95 | pbkdf2-v1/310000/16byte salt/256bitの独立JCA検証、256byte全長差 | 本番CPU/Java25でwarm-up後Login照合p95を測定。SS314の0.5～1.0秒から外れる場合security review。同一IDのparameterを変えない | 引継ぎ予定 |

| ITS-H-007 | Username key拡張migration・切戻し | SSC-014/V007の比較key96byte、表示/audit64byte、旧64byte拒否→DDL拡張、UK/NULL/境界、実Loginの独立PT | 既存schemaからV007へFlyway適用と復旧を実serverで確認。旧codeへ切戻す前にkey64byte超の有無を集計し、存在する場合は切戻し不可として運用判断。値の切捨て/再計算/削除で回避しない。JDK更新でUnicode増幅guardを再実行 | 引継ぎ予定 |

| ITS-H-008 | Transfer filesystem capability | SSC-019の実libc errno/no-replace/保持FD試験、本機Linux amd64合成fixture | 配備OS/CPU/libc、local filesystem/RENAME_NOREPLACE、procfs self FD、directory fsync、所有者0750/0640、systemd hardening下のnative accessとroot差替え拒否、kill/crash耐性。未検証network FS/非対応attributeはreadiness false。Java ATOMIC_MOVEへのfallback禁止 | 引継ぎ予定 |

追加（2026-09-08、SSC-019～022、PT-SCN-20260908-14）: writer/reader/完全metadata scan/診断startup probeの内部部品はlocal ext4＋mini/users合成fixtureで検証済み。Full root実体の非重複、single-instance/exclusive startup、probe→全scan→quota初期化→producer/HTTP開始の結線、Web read-only/API限定writeを実service UID/systemd hardening下で確認する。これらを本PTだけで完了扱いしない。

Probeの公開不確定/変質ready/清掃不能partは起動失敗の証拠として保全し、次回朝清掃・承認済み運用調査へ委ねる。新規dateのchgrp/fsync失敗でempty dateが残る場合がある。既存不一致をアプリ再起動でauto-chmod/chgrpして隠さず、運用者が状況と所有を確認して所定の修復/清掃を行う。業務readyの通常lifecycleは変更しない。Probe失敗後の再起動/運用復旧とsingle-instance競合は後続結線試験に含める。

## 3. 追加引継ぎ（正式47時点）

| ID | PG/PTの確認済み範囲と未完了 | 後続Linux IT/STの確認 |
|---|---|---|
| ITS-H-009 | private Inspectorの専用credential/保持inode/31応答保護・wrapper/oneshot契約を単体確認。親file publish・全結線は未完了 | 実root/UID/ACL/mount、4 previous-key profile、実credential配布、hardeningで同じ拒否条件を確認。秘密実体をGitへ保存しない |
| ITS-H-010 | flock/固定lockfile admission/停止状態読取/run byte/DB handoffを確認。親制御・SSC055永続原本・backup artifactは460残件 | 実停止・子終了・親再取得・reboot/timeout/再attempt・commit不明から復旧、設定公開とbackup restoreの結合を確認。単体の合成root属性を実配備合格にしない |

## 4. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-09-01 | 初期引継ぎ対象を登録。 |
