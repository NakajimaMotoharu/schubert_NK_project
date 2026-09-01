# PG・PT・IT工程引継ぎ事項

## 1. 目的・現在状態

確定済みRD/UI/SSを破壊せずにPG・PT・ITを開始・完了する条件、工程別成果物、実測で固定する値、未解決事項、
変更管理、実装上の禁止事項を一元化する。

- 上位設計: UI 261、263～265
- 関連RD: SYS-011、SCP-004～SCP-005、TST-001～TST-005、TST-101～TST-103、SCM-001～SCM-006、T-001～T-005
- 関連SS: 301、311～355、[361_RD・UI・SSトレーサビリティ](361_RD・UI・SSトレーサビリティ.md)
- QA/UIC blocker: なし。QA-041～044/UIC-001～004は承認・正本反映済み、RD変更/RDFはなし
- 工程実施gate: 355のCHR-G01～G06は2026-09-01に全件PASS。Current baselineとgate reportをproductionから分離して固定

## 2. 無断変更禁止のbaseline

1. Caddy→Web Java→Artemis→API Java→PostgreSQL/local file。Webから業務schemaへの直接accessは禁止。
2. Web/API間はJMS `BytesMessage`固定長電文だけ。256 byte header、64 layout、UI 233～236のoffset/length/typeを変更しない。
3. 現行14画面、21 GET mapping、現行URL、検索・表示・page・media/Rangeの利用者挙動をDIF-001～016以外で変更しない。DIF-016は現行session上限不具合をNKで修正する承認済み差分である。
4. USER/ADMINとowner scope、APIでの再検証、CSRF、暗号化永続session、8時間idle、最大2 sessionを維持する。
5. Sync 2秒、persistent、transacted session、Inbox/Outbox、operation token/HMAC、同一結果replayを維持する。
6. Internal asyncはConsumer 1/FIFO/business timeoutなし。RECEIVEDだけ取消可、初期`AnswerProvider`は空回答STUB。
7. Question/answerは論理削除、notification分離、backup成功・保持条件・FK確認後だけ物理削除。
8. Large resultは取得ACKなし、48MB/10,000 record上限、次朝削除。Mediaはlogical descriptorとWeb検証Range配信。
9. 単一server/DB/Broker、同時10名、p95 2.5秒、16GB/256GB、RPO/RTO 24時間、STANDARD modeを受入基準とする。
10. 毎朝の停止・PostgreSQL→backup→条件付cleanup→transfer→Artemis/Expiry→API→Web→Caddy順を変更しない。

変更が必要ならコードで先行せず、`8`の分類に従い正本とtest oracleを先に更新する。

## 3. PG開始条件

### 3.1 Pre-production gate

| Gate | 現在状態 | 開始条件 |
|---|---|---|
| SS正本 | 301～364作成・横断監査済、364の正式完了判定は完了 | 確定正本をbaselineとして維持 |
| QA/UIC | QA-001～044解決、UIC-001～004完了 | 承認済み設計とtest oracleを維持 |
| RDF | 0件 | 未処理RDF 0を維持 |
| Characterization | Artifact/baseline作成済、Current 23/23 PASS×2、差分0、CHR-G01～G06 PASS、gate commit `843de94` | Baseline/gate commitをproductionと分離して維持 |
| Git | Local `main`が正、meaningful commitで管理 | Clean worktree、gate commit特定、remoteはなくても開始可 |
| Environment | 設計値確定、minor/patch未実測 | Java 25/PostgreSQL 18/Artemis/Caddyの導入可能性とtoolchainを記録 |

Characterization harness、Maven Wrapper、toolchain、current baselineの作成はPG本体前のgate作業として許可するが、
NK production class、DDL、Flyway migration、production Caddy/systemd/Artemis設定を同じcommitへ混在させない。

### 3.2 Production PGの開始判定

`SS監査合格`、`QA-001～044解決・UIC-001～004完了`、`CHR-G01～G06合格commit`、`未処理RDF/UIC/重大QA 0`を全て満たした後、
開始判定者・日時・baseline/gate commit・対象release branchを記録する。SCM-006/T-005のGitHub remote作成待ちは
local Git/review/backupが有効なら開始blockerではない。

## 4. PG成果物・実装順

### 4.1 Module/artifact

| Module | 主SS | 必須成果物 |
|---|---|---|
| `schubert-nk-protocol` | 311、322～323 | 64 layout record/codec/schema/golden vector、共通error/value |
| `schubert-nk-api` | 311～312、314、321、324、331～333、352 | Consumer/application/repository/outbox/inbox/file/security |
| `schubert-nk-web` | 311～314、321、324、333、351～352 | Controller/form/template/view/session/JMS client/log outbox |
| `schubert-nk-batch` | 311、331～332、341、343、351～353 | Morning/backup/cleanup/migration verify/status |
| `program/characterization` | 355 | Current/NK共通harness、baseline、DIF/report |
| Infrastructure | 321、331、342～343 | Flyway SQL、Caddy/systemd/Artemis/PostgreSQL設定雛形、manifest |

CommonへHTTP form/view/entity/Repositoryを入れない。Web/APIが同じDB entity classを共有せず、wire recordとcodecだけを共有する。

### 4.2 実装順

1. CHR-G01～G06とcurrent baseline commit（2026-09-01完了）。
2. Root Maven Wrapper/toolchain/module boundary、CI相当local verify。
3. Common header/value/codecと64 layout/golden vector。
4. Flyway business/technical schema、role/grant、catalog verification。
5. API認証・検索・media descriptor・User、Inbox/Outbox/transaction。
6. Artemis明示Address/Queue/JMS client、sync Request/Reply、crash/retry。
7. Web session/security/form/controller/template、現行機能をCHR case単位で実装。
8. 質問/通知/回答/internal async/取消/論理削除、operation token。
9. File/Range/large result、朝batch/backup/cleanup/restore/status。
10. Caddy/systemd/credential/config/migration/cutover artifact。

各段階で影響CHR caseをNKへ実行し、未承認diffを後工程へ持ち越さない。

## 5. PG実装checklist

- 全public class/method/record/exceptionは311～324の責務・依存・引数・戻り値・transactionへ一致。
- 全template/controller/formは313のSCR/route/validation/role/state matrixへ一致し、inline JS/styleを作らない。
- 全SQLは331～332のquery ID、prepared binding、constraint/index/lock/owner scopeに一致。
- 全wire fieldは323のJava/DB/validation/変換規則へ一致し、offset/totalを重複手計算しない。
- Bodyは`BytesMessage`だけ。Object/Map/TextMessage、dynamic Queue、auto-create、nonpersistentを拒否する。
- Log/action/error/metricは351 catalogだけ。Password/context/body/path/secretを`toString`/exceptionへ出さない。
- Credentialは352/342の分離fileとkey versionを使い、Git、argv、unit `Environment=`、reportへ値を置かない。
- Migration/config/release/script/docは同一version/hash manifestへ入れ、productionで自動生成・自動推測しない。
- Test用failpointは試験build/profileだけで有効、production artifactに外部から到達可能なbackdoorを残さない。
- Code reviewでRD/UI/SS/test ID、禁止依存、security/transaction/crash後条件、CHR diffを確認する。

## 6. PT引継ぎ

### 6.1 Entry

対象実装・review完了、関連SSと354のcase実装、実PostgreSQL/必要な実Artemis/file fixture、credential、cleanup、
coverage matrixを準備する。H2/in-memory mockだけではcomponent PTを完了しない。

### 6.2 必須scope

- PT-CODEC: 256 byte header、64 layout、NFC/UTF-8/byte/padding/length/error profile/golden vector。
- PT-AUTH: 5/10回・15分、2/3 session、CSRF、AES-GCM、role/owner、Web業務DB grant 0。NKの3件目LoginはDIF-016に従い最古revoke・残り2件activeを必須とする。
- PT-IDEM/STATE: Message ID/token/HMAC、同異payload、取消race、論理/物理削除。
- PT-DB/SQL: 全constraint/index/role、境界、page/sort、optimistic/pessimistic lock、deadlock。
- PT-FILE/RANGE: root/symlink/TOCTOU/hash/atomic、200/201/10,000/10,001、Range/416。
- PT-BATCH/OPS/LOG/SECURITY: backup/cleanup/resume、config/secret、catalog/alert、canary漏えい0。

### 6.3 Exit

必須caseのfailed/flaky/skipped/not-run 0、要求/分岐/境界coverage 100%、重大不具合0、機密漏えい0、
release commitとmachine/report evidenceを固定する。PT結果で上位oracleを無断変更しない。

## 7. IT引継ぎ

### 7.1 Entry

PT exit達成、同一release artifact、実Java 25/Caddy/Artemis/PostgreSQL 18/systemd/file構成、credential、
障害注入・rollback・証跡容量・runbook rehearsalの準備完了を条件とする。

### 7.2 必須scope

1. 64 layout全件をWeb→Artemis→API→DB/file→Webで通し、wire/hash/DB/画面/logを相関。
2. DB commit/JMS send/ACK/Outbox markの各crash point、Broker/API/Web/DB停止・reboot、late reply取違い0。
3. Consumer 1/FIFO、取消race、初回＋3再配送、恒久error即DLQ、最終失敗job/DLQ整合、個別replay。QA-041/UIC-001承認済みの1/5/25秒で実施。
4. Web REQUEST outbox→WLGEVT01→DBをBroker/API再起動跨ぎで欠落/重複0。
5. Morning依存順、backup 7世代/失敗分岐、隔離restore、FK/cleanup、restart rate、DEBUG/STANDARD。
6. Path/Range/media 20 stream、Scenario 48MB、transfer/Queue/disk/memory容量境界。QA-042/UIC-002承認済みのAddress memory/page/page-full/disk-fullを実効configで検証。
7. 同時10名、p95 2.5秒、MQ待ち2.0秒、16GB/256GB budget、RPO/RTO 24時間。
8. USER/ADMIN/owner、CSRF/CSP/session/key、MQ ACL/DB grant/public port、secret/canary。
9. QA-043承認済みの専用backup roleで3 schemaをdump/restoreし、batch/backup roleの相互権限とkey非配布を負testする。

### 7.3 Exit

354のIT必須case、resource/restore/security/operational evidence、QA-041～042承認済み設定とQA-043承認内容を含む実効設定、
未説明DLQ/Queue/Outbox/Job 0、
重大不具合0、runbook実測更新を条件とする。

## 8. 発見事象・変更管理

| 発見内容 | 使用台帳 | 先行更新 |
|---|---|---|
| PG/PT/ITでSSだけの誤り・不足 | 914_詳細設計修正管理台帳 | 914→対象SS→code/test |
| UI外部仕様の修正が必要、RD影響なし | UIC＋QA | 913/911→UI→SS→code/test |
| RDの修正が必要 | RDF＋QA | 912/911→RD→UI/SS→code/test |
| RD修正に伴いUIも修正 | RDF＋UIC＋QA | 3台帳相互参照→全正本→code/test |
| Environment/実測値が設計上限内 | 実測記録、必要なら914 | Config manifest/runbook/test evidence |

SS工程完了後は914を使用できる。原因を`実装不具合`へ分類してSS/UI/RDの不整合を隠さず、逆に上位変更不要な
code bugへRDF/UICを乱用しない。Oracle/baselineだけを先に変更しない。

## 9. 後続で実測・固定する値

| 値 | 設計上限・初期値 | 固定工程・証跡 |
|---|---|---|
| Spring Boot/Artemis/PostgreSQL minor/patch | Java 25、PG 18、導入時安定版 | PG build manifest＋IT compatibility |
| Web/API JVM heap/direct/thread | 342初期値、16GB合計内 | IT GC/load/systemd memory report |
| PostgreSQL memory/connection/query timeout | 342初期値、pool 8等 | PT plan＋IT load/config snapshot |
| Artemis journal/paging/cache/window | 321初期値、SSD journal/paging 10GB・process 2GB budget、QA-042承認値 | IT File Journal/reboot/load/config snapshot |
| Query plan/index物理size | 331～332 query ID | PT/IT EXPLAIN・DB size report |
| Backup size/time・full restore RTO | 7世代/80GB、RTO 24h | IT/ST restore manifest/timeline |
| Full master migration/hash time | 59,627 file/19.24GB | Migration rehearsal report |
| OS user/group/mount/public IP/certificate | Allowlist/permission/TLS条件 | Installation manifest、no secret |
| Stop window/中止時刻 | UI 254手順内 | Rehearsal実測とGo/No-Go record |
| GitHub remote/CI credential | T-005、local Git暫定 | Repository作成連絡後、SCM record |

実測値がRD/UIの性能・容量・互換条件を満たさない場合は単なるtuningとして上限を広げず、`8`の変更管理へ移す。

## 10. Release・branch・証跡

- Mainをrelease可能に保ち、短命branch、review、local CI成功後に統合する。Gate/current baseline commitを履歴から失わない。
- Release tag、source、SBOM、jar、migration、config、systemd、script、doc、SHA256SUMSを1 manifestへ固定する。
- Asset、credential、runtime log、dump、backup、baseline以外の大容量実体をGitへ格納しない。
- PT/IT reportはrelease commit、environment/config/schema/protocol/credential version ID、case IDと相互参照する。
- Rollbackは343のcompatibility windowとforward-only migration方針に従い、production DBへ無計画なdown migrationを実行しない。

## 11. 実装・試験上の禁止事項

- Web業務DB直結、Browser→API/Artemis/DB/file直結、Caddyからasset/transferの直接配信。
- 固定長仕様をJSON/Java serializationへ置換、layout/field/長さ/URL/表示順をcode都合で変更。
- MQ auto-create/delete、dynamic/temporary destination、ObjectMessage、nonpersistent、AUTO_ACK、silent drop/purge。
- Inbox/Outbox/token/HMAC/owner再検証の省略、retryで同じ業務を二重更新、late replyを別requestへ渡すこと。
- Question/answer/notificationのcascade delete、backup失敗時cleanup、DLQ/Expiry/journal/WAL/file rootの直接削除。
- Security testのための認可/CSRF/暗号/redaction無効化、default/admin backdoor、secretのGit/env/argv/log/report格納。
- Characterization baseline/DIFをNK結果へ追従、failed/flaky/skippedを合格、current source/masterを書換えてbaseline取得。
- QA-041～044承認値からの無断変更、上位不整合を914だけで処理、またはSS自己修正を過去に遡って914へ登録。

## 12. 開始判定checklist

- [x] 363横断監査の必須項目が合格し、364のSS完了判定が成立。
- [x] QA-043/UIC-003を解決し、911/913、UI 212/251、331/341～343/352～354/361/363/364を一貫更新。
- [x] QA-044/UIC-004を解決し、DIF-016とCurrent/NK session oracleをUI/SS/Characterizationへ一貫反映。
- [x] 未解決の重大QA、RDF、UICが0。
- [x] CHR-G01～G06のcurrent baseline・gate report・review recordが存在。
- [ ] Git worktree clean、対象branch/release/gate commit、toolchain/environment、credential責任者が記録済み。
- [ ] PG責任範囲、PT/IT環境、変更管理、禁止事項を担当者が確認。

## 13. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | PG/PT/IT開始・完了条件、成果物、実装順、実測値、変更管理、禁止事項を作成。 |
| 2026-08-31 | 横断監査でQA-042/UIC-002をPG/IT開始・完了gate、容量試験、実装禁止事項へ追加。 |
| 2026-08-31 | QA-043/UIC-003の専用backup role/credential分離をPG開始gate、IT dump/restore・権限負testへ追加。 |
| 2026-09-01 | 未回答QA/UIC 3件を正式なPG開始blockerとして再確認し、関連正本・試験の反映先を同期。 |
| 2026-09-01 | QA-041/UIC-001承認済みの再配送値1/5/25秒をIT oracleへ固定し、残るPG開始blockerをQA-042～043/UIC-002～003へ更新。 |
| 2026-09-01 | QA-042/UIC-002承認済みのArtemis容量・paging値をIT oracleへ固定し、残るPG開始blockerをQA-043/UIC-003へ更新。 |
| 2026-09-01 | QA-043/UIC-003承認済みの専用backup role・credentialをIT oracleへ固定。QA/UIC blockerを解消し、production PGの残条件をCHR-G01～G06などの実行gateへ更新。 |
| 2026-09-01 | QA-044/UIC-004と`DIF-016`を反映。Characterizationを2回実行してCurrent 23/23 PASS、2回差分0、秘密情報hit 0、CHR-G01～G06全PASSを確認し、production PG開始の技術gateを解消。 |
| 2026-09-01 | SSC-001により§4.1のmodule名を311/343の正式artifact名へ統一。 |
