# 設定file・directory・初期data・migration・切戻し設計

## 1. 目的・追跡

Source/release/config/credential/data/log/runtimeの配置、環境差分、設定key、初期data、Flyway DB migration、
現行asset/metadata移行、切替・切戻しを実行前checkと証跡を含めて定める。

- 上位設計: UI 243、251、253～254、261、264
- 関連RD: SCP-002～SCP-005、MIG-DAT-001～MIG-DAT-008、MIG-001～MIG-008、SCM-001～SCM-006、
  FIL-001～FIL-005、TST-001～TST-005
- 関連QA/RDF/UIC: QA-007、QA-012～QA-016、QA-022、QA-024、QA-043、RDFなし、UIC-003
- 関連SS: [331_DB物理・DDL・index・権限設計](../330_データ・ファイル/331_DB物理・DDL・index・権限設計.md)、
  [342_Caddy・systemd・PostgreSQL・Java設定設計](342_Caddy・systemd・PostgreSQL・Java設定設計.md)

## 2. Directory・owner・Git管理

| Path | Owner/mode | 内容 | Git/release |
|---|---|---|---|
| `/opt/schubert-nk/releases/<version>` | root:schubert 0750、file 0640 | Immutable jar、DB migration、ops tool、manifest | Artifactはrelease package、sourceはGit |
| `/opt/schubert-nk/current` | root所有symlink | Active releaseへのatomic pointer | Git対象外、ターゲットversionはmanifest |
| `/etc/schubert-nk` | root:schubert 0750 | Rendered非秘密YAML/env/config manifest | TemplateだけGit |
| `/etc/schubert-nk/credentials` | root:root 0700、個別root:service 0600 | DB/MQ/AES/HMAC/backup credential source | Git/artifact/normal log禁止 |
| `/srv/schubert-nk/data/assets` | data owner:schubert-read 0750 | Scenario/audio/video/musicの永続実体 | Asset本体はGit禁止、manifestは取扱承認後 |
| `/srv/schubert-nk/data/transfer` | schubert-api:schubert-web 0750 | API `.part/.ready`、Web read | Git禁止、次回朝削除 |
| `/srv/schubert-nk/backup` | schubert-backup 0700 | 7世代dump/config | Git禁止 |
| `/var/lib/schubert-nk/artemis` | schubert-artemis 0700 | Broker instance/journal/paging | Git禁止、config templateはrelease |
| `/var/log/schubert-nk` | service group 0750、file 0640 | File logを使う場合のみ | Git禁止、journald優先 |
| `/run/schubert-nk/<service>` | systemd RuntimeDirectory | Lock/socket/temp metadata | Rebootで消去可 |
| `/srv/schubert-nk/staging/<run-id>` | migration user 0700 | 移行中asset/manifest、対象run限定 | Go/切戻し完了まで隔離 |

Directoryはprovisioningで明示作成し、application起動時に不明rootを自動作成/chmodしない。
Asset/transfer/backup/log/Artemis/stagingを同一または相互配下、またはsymlink接続しない。

## 3. Release package構成

```text
releases/<version>/
  web/schubert-nk-web.jar
  api/schubert-nk-api.jar
  batch/schubert-nk-batch.jar
  lib/schubert-nk-protocol.jar
  db/migration/V*.sql
  config/templates/*.yml
  config/caddy/Caddyfile.template
  config/artemis/broker.xml.template
  systemd/*.service
  systemd/*.target
  systemd/*.timer
  operations/bin/schubert-nkctl
  operations/runbooks/
  VERSION
  RELEASE-MANIFEST.json
  SHA256SUMS
```

`RELEASE-MANIFEST.json`はapp/protocol/schema/config version、Git commit/tag、JDK/build tool/dependency/BOM、OS対応、
全artifact hashを持つ。Release directory全fileを検証後にread-onlyにし、稼働中の上書きを禁止。

## 4. Config file・設定sourceの優先順

| 優先 | Source | 用途 |
|---:|---|---|
| 1（低） | Jar内default | 上位で確定済みの非環境値、安全なfail-closed default |
| 2 | `/etc/schubert-nk/common.yml` | protocol/timezone/monitoring共通 |
| 3 | `/etc/schubert-nk/<web|api|batch>.yml` | Process別port/pool/path/retention |
| 4 | `/etc/schubert-nk/<service>.env` | JVM option、config file location等の非秘密 |
| 5（高） | systemd credential/config tree | DB/MQ password、AES/HMAC key、backup recipient等のsecret |

Command line引数でapplication property実値を上書きしない。未知key、重複・非推奨alias、placeholder未解決、
secretのYAML/env格納、型/範囲不正は起動失敗。Effective configはsecret値を`<redacted>`にしcanonical hashを保存。

## 5. 主要設定key

### 5.1 Common・Web

| Key | Production initial | Validation/関連UI |
|---|---|---|
| `nk.protocol.version` | `001` | 完全一致、UI 232 |
| `nk.time.display-zone` | `Asia/Tokyo` | Wire/viewだけ、DB/JVM UTC |
| `nk.monitoring.mode` | `STANDARD` | STANDARD/DEBUG、UI 252 |
| `nk.web.http.address/port` | `127.0.0.1` / `8080` | Loopback |
| `nk.web.management.port` | `8081` | Loopback、Caddy非proxy |
| `nk.web.mq.reply-timeout` | `2s` | 100ms..2s、UI 212/253 |
| `nk.web.mq.wait.initial/max` | `12` / `20` | max<=20 |
| `nk.web.session.idle-timeout` | `8h` | UI 226、無断短縮禁止 |
| `nk.web.session.max-per-user` | `2` | APIが最終強制 |
| `nk.web.storage.asset-root` | `/srv/schubert-nk/data/assets` | absolute real dir/read-only |
| `nk.web.storage.transfer-root` | `/srv/schubert-nk/data/transfer` | absolute real dir/read-only |
| `nk.web.media.max-streams` | `20` | 1..20 |
| `nk.web.media.max-range-bytes` | `1048576` | UI 223/237と完全一致 |

### 5.2 API・JMS・DB

| Key | Production initial | Validation/関連UI |
|---|---|---|
| `nk.mq.url` | `tcp://127.0.0.1:61616` | Loopback/coreのみ |
| `nk.mq.sync-request/reply` | UI 231のAddress名 | 321のallowlistと完全一致 |
| `nk.mq.async-work/web-log/dlq/expiry` | UI 231のAddress名 | Unknown禁止 |
| `nk.api.sync-consumers.initial/max` | `4` / `8` | DB pool<=8 |
| `nk.api.async-consumers` | `1` | 固定、変更禁止 |
| `nk.db.url` | `jdbc:postgresql://127.0.0.1:5432/schubert_nk` | Loopback、parameter allowlist |
| `nk.db.pool.api.max/min` | `8` / `2` | UI 253 |
| `nk.db.pool.web.max/min` | `2` / `1` | UI 212の初期上限2、Technical schema専用 |
| `nk.db.connect-timeout` | `3s` | UI 212 |
| `nk.api.storage.asset-root` | `/srv/schubert-nk/data/assets` | read-only |
| `nk.api.storage.transfer-root` | `/srv/schubert-nk/data/transfer` | write、secure root |
| `nk.inbox.reference/update-retention` | `24h` / `7d` | UI 251、324 |
| `nk.outbox.sent-retention` | `7d` | PENDING/ERRORは無期限 |

### 5.3 Batch・backup

| Key | Initial | Validation |
|---|---|---|
| `nk.batch.zone/schedule` | `Asia/Tokyo` / `05:00` | systemd timerと照合 |
| `nk.batch.backup-root` | `/srv/schubert-nk/backup` | absolute real dir、other root非重複 |
| `nk.batch.backup-generations` | `7` | 固定、短縮禁止 |
| `nk.batch.transfer-cleanup` | enabled | 取得ACKなし、次回朝 |
| `nk.batch.expiry-retention` | `7d` | DLQに適用しない |
| `nk.batch.log-retention` | `90d` | Security hold除外 |
| `nk.batch.run-retention` | `400d` | FAILED調査中除外 |
| `nk.batch.chunk-size` | notification/question 1000、log 10000 | 1..defined max |

## 6. Credential catalog・rotation

| Credential ID | Consumer | 形式・rotation |
|---|---|---|
| `db-api`,`db-web`,`db-batch`,`db-migration` | 対応process | PostgreSQL SCRAM password、service別。`db-batch`はdumpへ使用しない |
| `db-backup` | backup unit | QA-043承認時の`schubert_backup`専用SCRAM password。`schubert-backup` OS userだけへ配布 |
| `mq-web`,`mq-api`,`mq-maintenance`,`mq-ops` | 対応process | Artemis credential、Address権限別 |
| `web-session-aes-current/previous` | Web | AES-256-GCM、key version付き |
| `web-revoke-aes-current/previous` | Web | Pending context revoke暗号、session keyと分離 |
| `api-context-aes-current/previous` | API | `auth_sessions.context_ciphertext`暗号、key version付き |
| `api-inbox-response-aes-current/previous` | API | Inbox replay response暗号、context keyと分離 |
| `operation-hmac-current/previous` | API | 256 bit以上、HMAC-SHA-256 |
| `web-log-aes-current/previous` | Web/API ingest | Technical outbox暗号 |
| `backup-age-recipient` | backup unit | 公開keyのみserver保持、private keyはoffline |
| Caddy TLS key/state | Caddy | Caddy専用OS権限、fingerprint管理 |

Symmetric keyは最低32 byte、自動生成passwordは最低32 byte相当のCSPRNG出力とし、ID/versionと有効日だけmanifestに記録。Rotationは「previousを配備→current切替→
旧ciphertext/HMAC保持期間の読取確認→previous除去」の順。Unknown key versionはdeny closed、運用介入とする。

## 7. 環境差分

| 項目 | Local dev | PT/IT | Production |
|---|---|---|---|
| PostgreSQL/Artemis | Container/専用instance可、実製品同major | Java 25/PG18/Artemis導入minor | 単一server、loopback |
| DB | 個人専用DB | Testごと初期化 | `schubert_nk`、real data |
| Port/root | Workspace専用非衝突値 | Test host専用 | 本書のdefault |
| Credential | Test限定のrandom secret | CI secret store | systemd credential、0600、Git禁止 |
| TLS | Loopback/test CA | Test CA | Caddy internal CA/IP |
| Monitoring | DEBUG可 | DEBUG/STANDARD両方 | STANDARD |
| Asset | 最小fixture＋必要時read-only copy | Full sanitized/real authorized copy | Full 59,627 file baseline |

H2、in-memory JMS、UTF-8以外のwire、relaxed validation、ADMIN固定passwordでPostgreSQL/Artemis/securityを代替しない。
環境差分は`config/environment-matrix.yml`のallowlistと本表を照合し、業務仕様のprofile分岐を作らない。

## 8. 初期data

### 8.1 Migration固定master

| Data | 値 | 検証 |
|---|---|---|
| `games` | `(1,NUKITASHI1,NUKITASHI,1)`、`(2,NUKITASHI2,NUKITASHI2,2)` | 2件、code/order UK、UI 223一致 |
| Code/state/role | DB CHECKとJava enum | 全enumのDB/Java/wire照合 |
| Schema history | 期待Flyway version | checksum/installed rank正常 |
| MQ Address/Queue | 321の6組 | Auto-createではなくconfig初期化 |

### 8.2 Bootstrap account

- 現行`user_pass.txt`を移行せず、初期ADMINを安全なoneshot `schubert-nk-bootstrap-admin.service`で1件作成。
- Username/passwordはsystemd credentialから読み、passwordは画面と同じvalidation、`{pbkdf2-v1}`でhash化し、平文はmemory使用後zero。
- `app_users` 0件の場合だけ実行、複数回/既存Userありは無変更でexit 20。固定default passwordなし。
- 作成後に別sessionでLogin・password変更・ADMIN権限を確認。Bootstrap credential sourceは承認済み手順で無効化/削除。

## 9. Flyway migration

### 9.1 責務分離

- Migration実行は`schubert_migration`が`nk_owner`へ限定SET ROLEするoneshot。API/Web起動時にmigrate/repair/cleanしない。
- History tableは`schubert_meta.flyway_schema_history`、`validateOnMigrate=true`、`outOfOrder=false`、
  `baselineOnMigrate=false`、`cleanDisabled=true`。Migration checksum変更をrepairで隠さない。
- Application起動はmanifestのexpected schema version/checksumとDB historyをread-only検査し、不一致はreadiness false。

### 9.2 Initial sequence

| Version群 | 内容 | Transaction |
|---|---|---|
| V001 | extension/schema、owner/default privileges | DBA事前作業と分離 |
| V002 | Account/session/master table、PK/FK/UK/CK | 1 migration transaction |
| V003 | Question/message/log/batch/Web technical table | 1 migration transaction |
| V004 | Btree/partial index、小規模initial data | transaction |
| V005 | GIN/pg_trgm index、grant/view | Full data load前は必要indexだけ、後続で最終化 |

実装時の実version番号は上記責務順を崩さず、1つの巨大migrationへ集約しない。
`CREATE INDEX CONCURRENTLY`等のtransaction外DDLが必要な場合は個別migrationに分離し、失敗/再開手順を追記。

## 10. 現行data移行・inventory

| 対象 | Current baseline | NKの検証 |
|---|---:|---|
| Master file/総byte | 59,627 / 19,240,707,190 | 全file count/byte/SHA-256 |
| Scenario file/entry | 262 / 99,661 | DB count、display order、代表検索 |
| Audio metadata/link | 37,256 / 35,201 | File/hash、orphan/game不一致0 |
| Video | 20 | Stable logical ID/category/pair/order、Range |
| Music | 129 | SHA-256 logical ID、section/pair/order |
| Current log/account | 非移行 | NKは初期event/新規accountだけ |

### 10.1 ETL順

1. Current source/program/DB/materialのcommit/hash/path/mtime/size/countをread-only inventory。作業copyをstagingへ作る。
2. File pathをNFC・root-relative storage pathとsanitized display pathへ分離。絶対/path traversal/NUL/control/symlinkを拒否。
3. SHA-256/byteとcategory/pair、現行ID→NK ID/display order対応表をcanonical manifestへ作成。
4. `pg_temp`のstaging tableへCOPYし、件数・型・NFC/byte・参照を検査。Targetが空の初期DBへ1 transactionでinsert。
5. GIN/final index作成、ANALYZE、全FK/CK/UK/orphan/game不一致・link順を検査。
6. Asset staging全fileをmanifestで照合後、application停止中に確定asset rootへ同filesystemでatomic切替。
7. CHR、UI 254受入、backup/restore、morning runをrehearsalし、所要時間/disk peakを記録。

ID再採番は可だが、現行順を`display_order`に固定し、対応表をmanifestに残す。
Current bookmarkのDB ID互換を新しい要件として暗黙追加しない。

## 11. Deploy・application rollback

### 11.1 Deploy

1. Releaseを新version directoryへ配置、owner/mode/`SHA256SUMS`/manifest/signatureを検証。
2. Rendered configをstaging pathでschema/secret/path/port検証。Caddy/systemd/Artemis/PostgreSQLのvalidatorを実行。
3. Backup・停止・Flyway migrate・実効schema/grant検査。
4. `/opt/schubert-nk/current.new`を新releaseへ作り、`renameat`/`mv -T`相当で`current`をatomic切替。
5. Morning dependency順でstart/readiness/smoke、release/config/schema/protocol versionの一致を確認。

### 11.2 Application rollback

- Trigger: Startup/readiness、major functional/security/performanceのGo不可、またはmigration incompatibility。
- Caddy停止→Web/API/Artemis停止→NK可変data dump保全→schema compatibility判定。
- 旧applicationが新schemaを読めるadditive migrationなら`current`を旧releaseへatomic切戻し。
- 読めない場合は当日backupを別restore DBへ検証後、承認済みrestore手順でDB全体を戻す。Down migration/手修正しない。
- Rollback後も新release/config/data dumpを隔離保全し、調査前に上書き/削除しない。

## 12. 現行からの切替・切戻し

### 12.1 Cutover gate

- RD/UI/SSとQA/RDF/UICが必要状態、CHR baseline/harness、PT/IT/ST、full rehearsal、restore test、
  public 55160/TLS、定量count/hash/performanceが合格。
- 停止枠、Go/no-Go/切戻し判定者、判定期限、利用者周知、現行backup保持期間が承認済み。
- 現行program/DB/config/asset/Caddy/NAT/start手順はread-only保全し、NKが上書きしない。

### 12.2 Sequence

```text
Go一次判定
 -> 現行public入口停止
 -> 現行app停止＋最終inventory/hash/DB backup
 -> NK asset/DB最終load＋manifest照合
 -> NK PostgreSQL -> Artemis -> API -> Webのinternal acceptance
 -> Caddy/NAT 55160をNKへ
 -> external acceptance
 -> Go最終判定または切戻し
```

切戻し判定完了まで受入担当者以外の更新業務を開放しない。現行/NKを同時に本番更新可能にしない。

### 12.3 Rollback trigger・手順

Triggerはdata hash/count/FK不一致、Login/検索/media不能、message取違え/重複更新/質問消失、
security境界違反、backup/recovery不成立、公開TLS不能、停止枠内で是正不可能な性能未達。

1. NK Caddy停止、更新遮断。Web/API/Artemis停止。
2. NK切替後可変dataをtimestamp/manifest付きdumpとして隔離保全。現行へ自動マージしない。
3. 現行DB/program/config/asset hashを照合し、保全済み手順で起動。
4. Login/検索/Scenario/audio/video/music/logのsmoke、Caddy/NAT 55160/TLSを現行へ戻す。
5. External smoke後公開。原因、NK保全data、失われ得る更新、利用者影響、再計画を記録。

## 13. Migration/rollback証跡

- Source/target host、current/NK Git commit/tag、release/config/schema/protocol version、tool/hash、operator/判定者・日時。
- File count/byte/SHA-256、DB table/constraint/orphan、mapping count、表示順、CHR/test result、duration/disk peak。
- Backup/restore manifest、Caddy/NAT差分、public certificate fingerprint、Go/no-Go/rollback判定と根拠。
- Password/key/質問本文、credential実値、許諾上不要な個人・著作物pathは証跡へ出さない。

## 14. PT・IT・Rehearsal

- Configの未知/重複/範囲外/missing secret、root/port重複、effective hash drift、production profileのdebug設定。
- Clean OSでdirectory/owner/mode/systemd credential/release配置を再現、serviceごとの読み書き権限負test。
- Flyway validate/migrate/checksum mismatch/out-of-order/partial failure、applicationの自動DDL禁止、旧/new releaseのschema compatibility。
- Current full inventory、不正path/symlink/hash、件数差、ID再採番/display order、再実行、staging失敗・容量・中断。
- Release current切替直前/直後のkill、migration後旧app、backup restore、NK可変data保全、current公開への切戻し。
- 最低1回の全量rehearsalで所要時間、disk peak、停止枠、判定時刻を実測しrunbookに固定。

## 15. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-039 | Config優先順をjar default→common→service→env→credentialに固定し、unknown keyを起動失敗 | 環境差分とsecret分離を再現可能にし、typo黙認を防ぐ | ConfigurationProperties/schema test |
| SS-D-040 | Flywayはapplication起動時validateのみ、migrateは専用oneshot、clean/repairは自動禁止 | 起動中DDL・checksum改ざんを防ぎ、rollback判定を明示 | Migration pipeline/IT/runbook |
| SS-D-041 | Current/NK切替中の一般更新を最終Goまで許可しない | 二重更新・自動マージ不能なNK質問/account差分を防止 | Cutover運用・ST acceptance |

## 16. 禁止事項

- Secret/asset/dump/log/runtimeをGit/release artifactへ含める、またはproductionの実値をdocument/templateに書くこと。
- Application起動時DDL update、Flyway clean/repair自動、適用済みmigrationのchecksum書換え、手動down migration。
- Current source/dataを移行toolから更新する、現行/NKを同時本番更新可能にする、Go前に現行保全を削除。
- 対象DB/root/release versionを識別せず、広範囲削除・schema drop・restoreを行うこと。
- H2/in-memory MQだけでPG/ITを合格、または環境profileでrole/owner/validationを無効化すること。

## 17. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | Directory/config/credential/initial data/Flyway/current migration/cutover/rollbackを詳細化。 |
| 2026-08-31 | 横断監査でmigration DB role名をUI 212の`schubert_migration`に統一。 |
| 2026-08-31 | 横断監査でWeb DB poolをUI 212の上限2へ修正し、Web revoke/API context/API InboxのAES keyを用途別に分離。 |
| 2026-08-31 | DB dump credentialをbatch保守用から分離する`db-backup`候補をQA-043/UIC-003回答待ちで追加。 |
