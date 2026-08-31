# 障害検知・復旧runbook

## 1. 目的・適用原則

Web/Caddy/API/Artemis/PostgreSQL/file/backup/batch/config/credentialの障害に対し、検知、影響封じ込め、
証跡保全、復旧、整合確認、公開再開の一貫した手順を定める。

- 上位設計: UI 213、231、237、251～252
- 関連RD: AVL-003～AVL-010、OPS-011～OPS-017、MON-001～MON-009、BAK-005～BAK-008
- 関連SS: [321_Artemis物理構成・JMS設定設計](../320_メッセージング/321_Artemis物理構成・JMS設定設計.md)、
  [341_朝batch・backup・削除・再実行設計](../340_batch・基盤/341_朝batch・backup・削除・再実行設計.md)、
  [351_Log・metric・alert・error code設計](<351_Log・metric・alert・error code設計.md>)
- 関連QA/RDF/UIC: QA-021、QA-027、QA-029、QA-033、QA-038～QA-039、QA-041～QA-043、UIC-001～UIC-003。Broker容量とbackup role境界を確認中

自動復旧はprocess restart/outbox retry/JMS redeliveryの設計済み範囲だけ。DLQ再投入、DB restore、
credential差替え、不明file削除、強制終了、public再開は運用者が証跡と対象を確認して行う。

## 2. Severity・役割・記録

| Severity | 条件例 | 入口 | 一次応答目安 |
|---|---|---|---:|
| SEV-1 | Security境界違反、data消失/不整合、DB/asset全体不可、disk 95%、切戻し要 | Caddy即停止/非公開 | 15分 |
| SEV-2 | API/Web/Broker継続不可、DLQ増加、backup 2回失敗、integrity mismatch | 原則maintenance/503 | 30分 |
| SEV-3 | 単一media欠落、個別cleanup失敗、warning threshold | 対象機能のみ停止可 | 1時間 |

Incident IDを`INC-yyyyMMdd-NNN`で発行し、開始/検知時刻、severity、判定者、host/release/config/schema、
alert/error/action、request/message/correlation/receipt ID、実施操作、前後状態、利用者影響、公開再開判定を記録。
Password、token、body、secret、physical path全文はincident記録に含めない。

## 3. 全障害の初動

1. 現在時刻とincident IDを固定。後のcommand/outputへ同IDを付与。
2. `schubert-nkctl status --read-only`相当でunit/readiness、public/loopback、Queue/DLQ/Expiry、DB、disk、last backup/batch、release/config/schemaを取得。
3. Data/security/広範囲影響または原因不明ならCaddyをmaintenance/停止にし、新規requestを遮断。
4. Journald/application log/Artemis management/DB stats/batch manifestの必要範囲をread-onlyで保全。Log rotation前にhashと時間範囲を記録。
5. 直前のdeploy/config/package/morning run/disk/resource変化を確認し、推測と事実を分ける。
6. 該当runbookの事前条件・対象ID/path/DB/Queue・backupを確定後だけ変更操作。
7. 復旧後はinternal smoke→整合check→external smokeの順。原因未撤去、DLQ未整合、secret漏え未調査で公開しない。

## 4. RB-001 Web/Caddy障害

- Public TLS 55160、Caddy active/config/certificate、Web loopback 8080/readiness 8081、MQ reply Consumer、technical DBを順に確認。
- Caddy 502/503、Web timeout、session decrypt、outbox oldest、FD/thread/memoryを別々に分類。
- Web unitの自動restart成否と10分5回rate limitを確認。起動loop中に手動restartを連打しない。
- Config/schema/key version不一致はvalidated release/config/credential manifestに戻し、暗号sessionを一括削除しない。
- MQ/API障害ならWebのみrestartせず依存側を先に復旧。Logout revocation row/Web log outboxの滞留を残してretry。
- Web readiness、Login表示、既存session、USER/ADMIN、MQ request/reply、REQUEST投影をinternal確認後、Caddyをvalidate/start。

完了条件: Public `/login` 200/TLS/header、既存または明示Login再開、late reply取違え0、outbox減少、restart継続なし。

## 5. RB-002 API障害

1. Consumer count 0、API readiness、JVM exit/OOM/protocol error、DB/MQ/asset root、restart rateを確認。
2. API停止中のrequest/workはdurable Queueに滞留させ、Queueをpurgeしない。Webは503、更新はoperation tokenを維持。
3. Protocol errorならRB-004、DBならRB-005、fileならRB-008へ分岐。OOM/resourceはleak/入力/同時数/metricを調査する。
4. 原因撤去後、API start→DB/MQ/root/codec/Consumer readiness→Queue減少・Inbox/Outbox・Question stateを確認。

完了条件: Sync 1往復、Async FIFO/duplicate 0、outbox減少、RECEIVED/PROCESSINGの説明不能滞留0、新規DLQなし。

## 6. RB-003 Artemis/Broker障害

- Unit/exit、bind 61616/8161、journal load/sync、disk/inode、Address/Queue/consumer/message/delivering/scheduled、DLQ/Expiry、config/security driftを確認。
- 再配送はQA-041/UIC-001承認値の1秒、5秒、25秒を正常値とする。実効configまたは観測時系列が異なる場合はconfig driftとして扱う。
- QA-042解決までAddressの`BLOCK`/`PAGE`、memory high-water、page limit/page-full値の差を無断で故障復旧に使用しない。実効config、
  address memory/page byte/page file、global memory、filesystem率を同時に保全する。
- Caddy/Web/APIを停止または非公開にし、producer/consumer I/Oを止める。
- Disk不足ならRB-006。Config driftならvalidated `broker.xml`/credentialへ戻し、journal fileを直接編集/削除しない。
- Clean restartし、journalの回復、全6 Address/Queue/durable/routing/security、duplicate cache、disk、consumer 0時の件数を確認。
- Expiry保守を必要時再実行、API→Web→Caddy順で起動。Queue減少、redelivery、Inbox冪等性を監視。

Journal破損の自動初期化をしない。新broker instanceへ移す場合はDB Inbox/Outbox/async jobとQueueの
整合復旧計画をSEV-1承認で実行する。

## 7. RB-004 Protocol error・DLQ

### 7.1 Browse/triage

1. DLQはoriginal Address/Queue、transport/business/correlation ID、layout/version、delivery count、error code、detected service/timeをbrowse。Bodyは原則dumpしない。
2. `request_inbox`、`mq_outbox`、`async_jobs`、`notifications`、`answers`をIDでread-only照合。DB commit済み/未定を判定。
3. 同種件数、producer/service version、config/protocol checksum、直前deploymentを確認。Poison messageかproducer系統障害かを分離。

### 7.2 再投入/整合

- 原因修正、codec test、承認された対象business Message ID・件数・操作者・incident IDなしに再投入しない。
- RequestがDB完了済みなら同Message IDでreplay。未処理なら同ID/bodyをoriginal Addressへ1件ずつ。Bodyを手編集しない。
- Internal workでDBがERROR確定済みなら自動再処理しない。RECEIVED/PROCESSINGでBrokerだけDLQなら、
  (a) same ID再投入、または(b) job/notification ERROR同transaction確定のいずれかを承認。
- 再投入後の新transport ID、Inbox/Job/Notification/Answer、Queue/DLQを確認してから元DLQを個別削除。

Login request DLQはpasswordを含む可能性がある。Bodyをterminal/ticket/fileへ出力せず、アクセスを限定し調査後に
再投入不要であることを確認して承認削除。

## 8. RB-005 PostgreSQL障害・restore

### 8.1 障害復旧

1. Caddy/Web/API/batchを非公開/停止。`pg_isready`、unit、disk/inode、WAL/checkpoint、connection、schema/config、DB logをread-only確認。
2. Connection枯渇はclient leak/long transaction/lockをIDで調査。根拠なくbackend terminate/max_connections増加をしない。
3. PostgreSQL標準crash recovery後、schema history/constraint/index/role/grant/sequence、read/write probe、Inbox/Outbox/Jobを確認。
4. ArtemisとDB状態を照合、API→Web→Caddy。JMS redeliveryでrollback済みが復元され、commit済みがInbox replayになることをsample。

### 8.2 Backup restore（SEV-1・承認必須）

1. Restore pointのmanifest/hash、DB/app/schema/config version、取得日時、想定データ損失範囲/RPOを確定。
2. 元DB/data directoryを上書きせず、まず隔離test DBへ`pg_restore`。List/hash/schema/count/FK/constraint/orphan/代表業務を検証。
3. 本番restore対象host/database名を二者確認。現DBの最終保全dump/log/Queue状態を隔離。
4. Validated runbookで新DB instance/databaseへrestore、role/grant/sequence/schema versionを復元。Applicationの自動migrationで合わせない。
5. Restore後のArtemis messageはDBの過去状態とずれるため、Inbox/Outbox/Question/Jobごとに整合判定。一括purgeしない。
6. Internal acceptance＋Characterization smoke＋backup再取得後、判定者がpublicを再開。RTO計測を証跡化。

## 9. RB-006 Disk・memory・resource枯渇

| 状態 | 自動/即時 | 復旧原則 |
|---|---|---|
| Filesystem 80% | Warning | directory別容量、growth rate、backup/log/transfer/Artemis/DBをread-only調査 |
| 90% | Critical | Large-result・質問新規を9001、95%は入口停止 |
| JVM OOM/MemoryMax | Process exit/restart | Leak/入力/同時数/metricを分析、heap dump自動生成なし |
| Queue high-water/page-full/block | QA-042承認済みpolicyによるpagingまたはproducer例外/timeout、9001、outbox retry | Consumer/依存復旧、message削除なし。Memory/page/diskを分けて診断 |

削除は保持期間済み・正規root・通常file/row・backup gate・対象IDをread-onlyで確定したものだけ。
DLQ/PENDING/ERROR/PROCESSING、最新/既存7世代backup、asset、DB/WAL/journal、transfer root自体を直接削除しない。

## 10. RB-007 Backup/morning障害

- Backup失敗はbusiness/technical data cleanupをskip、transfer cleanupとapplication起動は続行。失敗を無視成功化しない。
- Root/permission/capacity/DB/pg_dump/list/hash/config encryption/atomic renameのerror codeで分類。既存7世代を保護。
- `permission denied`は実効DB user、credential ID、dump対象schema/table grantを値非表示で確認する。QA-043回答前にbatch roleへSELECTを追加して復旧しない。
- 原因撤去後、新directoryで`backup`stepを再実行。同日成功をmanifest/DBで確認してから
  `morning-run --resume <runId>`で元cutoffのcleanupを再開。
- Transfer root safety failureはapplicationを起動しない。Individual cleanup warningは容量と対象typeを調査後、同runで再実行。
- Package update/reboot失敗はboot/dpkg/filesystemの安全を確認。手動強制reboot/killは証跡と中間transaction判定後のみ。

## 11. RB-008 File/media integrity障害

1. Webは対象streamをopenせず404/503、API/DB更新なし。Logical ID/file ID、descriptor、検証step、expected/actual size/hashの比較結果を証跡化。
2. Root/symlink/permission/mount異常なら対象全配信を停止。単一asset欠落/hashなら対象だけ停止しmanifest正本を確認。
3. Assetは保存済みmaster正本からstagingへ復元、count/size/SHA-256/metadataを照合後、application停止中に対象をatomic差替え。
4. Transfer `.part/.ready`は自動修復せず、参照requestの同token/Message ID処理でmasterから再生成。旧fileは次朝清掃。
5. Size/hash/Range、CHR-M01/M04/M07、監視を確認後配信再開。

## 12. RB-009 Credential・crypto・security incident

- `SECRET_MISSING`/key version/tag不一致はdeny closed、対象session/outbox/inboxを自動削除しない。
- 漏え疑いはSEV-1、Caddy非公開・credential access遮断・証跡保全。値をincident channelへcopyしない。
- 影響credentialのconsumer/data scope、最初/最後アクセス、log/data漏えを調査。DB/MQ password、AES/HMAC、TLSを別々に扱う。
- Current/previousのrotation順で新keyを配布、新規writeを切替、旧dataを読める期間を維持。即時失効が必要なcontext/session/passwordは全revoke/reset。
- Re-encryptを手編集SQLで行わず、version付き専用migration/tool・二人承認・backup・件数/tag検証。

## 13. RB-010 Config/release drift

1. Effective config hash、release SHA256SUMS、Git commit/tag、schema/protocol、systemd/Caddy/Artemis/PG実効値をread-only比較。
2. Secret値ではなくID/version/permission/hashを比較。Driftの作成者/時刻/理由が承認証跡にあるか確認。
3. 未承認driftは現状を保全後、validated release/configをstagingでrender/validateし、計画停止で戻す。
4. DBへdown migration、Artemis journal初期化、secret自動生成、不明configの上書きは行わない。

## 14. 全体disaster recovery

単一serverでHAなし、RPO/RTO 24時間、local backupは同一SSD故障を保護しない。Assetは別保存正本とmanifestから復元。

1. Clean OS/JDK/Caddy/PostgreSQL/Artemis/service account/directory/firewallをrelease/provisioning manifestで再構築。
2. Release artifact/config非秘密/credentialを承認済み正本から配備、hash/owner/mode。
3. Assetをmaster manifestから復元、59,627 file/19,240,707,190 byte、DB metadata対応を検証。
4. PostgreSQLを新instanceへrestore、schema/constraint/role/countを検証。
5. Artemisは保全済みconsistent journalがなければ新instanceを定義。DB Inbox/Outbox/Jobから未確定処理を個別整合。
6. Morningの依存順で起動、full integrity/CHR smoke/security/performance/backup再取得、Go判定。

RPO/RTO計測は検知からpublic再開まで。復旧で失われるaccount変更/質問/通知/logの範囲を明示する。

## 15. 公開再開checklist

- [ ] 原因が撤去または承認済み封じ込め、severity/残risk/利用者影響が記録済み。
- [ ] Release/config/schema/protocol/credential version、directory、disk/memory、全unit/readinessが一致。
- [ ] Queue/DLQ/Expiry、Inbox/Outbox/Job/Notification、DB constraint、asset/transferに説明不能な不整合がない。
- [ ] USER/ADMIN Login、sync、async stub、search、media/Range、REQUEST/audit log、backup/statusのinternal smoke合格。
- [ ] Security/secret/integrity事象は必要なrevoke/rotation/canary、DLQは再投入/保留/削除判定済み。
- [ ] Caddy validate、public TLS 55160/header/login、外部smoke、判定者/日時を記録。

## 16. Runbook rehearsal・更新

- ITでRB-001～010の対象障害を少なくとも1回、DB restore/full disasterはrelease前・月次の隔離環境で実施。
- Command実値、所要時間、権限、実効threshold、失敗点、判定順は実測後に証跡付きで本書を更新。
- 手順の結果が上位仕様と異なる場合、workaroundを永続化せずQA/RDF/UICまたはPG工程の変更管理へ移す。

## 17. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-048 | Data/security/原因不明障害はCaddyで先に新規requestを遮断し、証跡保全後に復旧 | 新規更新と証跡rotationが影響を広げることを防止 | Incident template、runbook IT |
| SS-D-049 | DLQは元messageを編集せず同Message IDで個別再投入、DB整合確認後だけ元を削除 | Inbox/Outbox冪等性を利用し、二重業務・証跡消失を防止 | Ops tool/approval/DLQ IT |
| SS-D-050 | DB restoreは隔離test DBで検証後、現状保全と二者対象確認を必須 | 広範囲の上書き・誤restoreを防止しRTO証跡を残す | Restore tool/rehearsal/release gate |

## 18. 禁止事項

- 対象未確定の再帰削除、DB/schema drop/restore、Queue/DLQ/Expiry purge、journal/WAL/data file直接操作。
- 調査のためのfixed body/password/token/secret/heap dumpをterminal/ticket/共有領域へ出力。
- Restart連打、systemd rate limit迂回、証跡/中間transaction確認なしのSIGKILL/reboot。
- 原因未撤去、整合不明、新規DLQ/integrity/secret alertを残した公開再開。

## 19. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | Component、DLQ、DB restore、resource、backup、file、credential、drift/disasterの復旧手順を作成。 |
| 2026-08-31 | 横断監査でQA-042/UIC-002を追跡し、Artemis memory/page/disk容量故障の証跡と切り分けを追加。 |
| 2026-08-31 | QA-043/UIC-003のbackup role/grant障害を値非表示で切り分け、batch roleへの緊急SELECT追加を禁止。 |
| 2026-09-01 | QA-041/UIC-001承認を反映し、Broker再配送の正常時系列を1秒、5秒、25秒へ固定。 |
