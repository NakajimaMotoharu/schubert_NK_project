# IT・ST引継ぎ事項

## 2026-10-09 当source普通親の実測引継ぎ（PG/PT限定・IT/ST未実施）

現正式はPT-WEB-20260925-24/1964PT/53scopeのまま。新candidate1ec19782a/PG715/schema028はhost3502PT517suite/static6zero、当ordinary55ac sameRootAPI-Web-Caddy/実CurrentA01/真正PID1-RootDONE/ownedstop/全24資源0/八nativeを限定検証済みだが、全四coverage100/全CHR/正式工程は未完了。下段9/20以前の正式・割合は履歴で現在率に使わない。

PG725 original1800sで1794.547089s（余裕5.452911s）、旧PG693 source9bd1752.251786s（別sourceで比較性能認定0）。PG734の一回owned診断ではpermit発行→保持Backup/DB→RootUnit再検証中。Linux serverで同一source・同所有契約/元budgetを保持して起動所要、CPU/DB/Unit・artifact確認の内訳、負荷変動、失敗後逆順停止/復旧、長期運用を測定する。PG/PTだけで性能/ST合格やbudget緩和を宣言しない。今回VMの単発値をp95/RTOへ換算しない。

2026-09-20 最新確定: 正式PT-WEB-20260920-27/source3b980d71f5573342b7c787ad6eed53db6d8c2940、10:14:36～10:27:24 JST/Maven12:47/exit0、全1719PT（Protocol80/Storage82/API689/Web460/Batch367/CHR41）、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review継続・coverage除外追加なし、CHR SpotBugs未設定。JS1file全line/function/branch100%、18collector/41scope整合・81負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST2/16＋ASY1/5＋Web25/219＝99部分成果929PT（全1719の内数）、今回再開比+304PT/+34部分成果。PG215 Log画面状態8PT・PG216実template8PTを限定認定、BUG226/YKT182完了。LogのBrowser入力検査/ADMIN HTTPは未実装。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/残Web・本文controller-file/readiness/Logout/QA045/実NKgateは未完了。固定加重40.85～52.35%（中心46.6%≒47%、約41～52%）を維持。残量9%で利用者指定の停止、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

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
