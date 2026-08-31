# PT・IT試験観点詳細設計

## 1. 目的・状態・追跡

詳細設計からPT（単体試験）・IT（結合試験）へ引き継ぐ分岐、境界値、異常系、競合、再送、権限、
性能・復旧の試験条件とoracle、証跡を定める。本書は試験codeではなく、後続工程の実装・実行契約である。

- 状態: `確認待ち`。Broker再配送第3間隔のoracleだけQA-041/UIC-001回答待ち、その他は確定
- 上位設計: UI 213、221～254、261、264
- 関連RD: TST-001～TST-005、TST-101～TST-103、T-001～T-004、PER-001～PER-010、AVL-003～AVL-010
- 関連SS: 311～353、[355_Characterization Test実行準備・PG開始gate](<355_Characterization Test実行準備・PG開始gate.md>)
- 関連QA/RDF/UIC: QA-001～QA-041、RDFなし、UIC-001

## 2. 試験階層・環境

| 階層 | 対象 | 外部依存 | 必須実行環境 |
|---|---|---|---|
| PT-pure | record/value/codec/validator/mapper/state machine/Range/parser | なしまたはin-process fake | Java 25、pinned Maven Wrapper |
| PT-component | Repository/migration/security/session/outbox/batch step | 実PostgreSQL 18、実file system、必要に応じ実Artemis | Containerまたは隔離local instance |
| IT-interface | Web→Artemis→API→PostgreSQL/file | 全component実process | Java 25、Artemis、PostgreSQL 18、Caddy |
| IT-operational | systemd/morning/backup/restore/resource/security | 実OS unit・volume・port | 16GB/256GB構成相当の隔離環境 |

H2、in-memory Queue、ObjectMessage、file代わりのbyte arrayだけで、PostgreSQLのconstraint/lock、Artemis File Journal/
transaction/redelivery、file systemのsymlink/atomic renameを合格扱いしない。テスト固有profileでproductionの認可・暗号・
redactionを無効化しない。

## 3. 共通試験契約

各caseは`Test ID`、関連RD/UI/SS、事前条件、入力・故障点、実行手順、期待HTTP/wire/DB/MQ/file/log、
後条件、実測値、証跡path/hashを持つ。時間依存caseは制御clock、並行caseはbarrier/latch、crash caseは
明示的failpoint名で再現する。`Thread.sleep`の長さだけに依存する合否判定を禁止する。

- 同一fixtureの初期化とcleanupをcaseごとに実行し、実行順依存をなくす。
- 期待errorはexception classだけでなく、wire result/HTTP、DB/MQ/fileの非更新、audit/error codeまで確認する。
- 機密値はfixtureに一意canaryを使い、log/metric/report/DLQ/property/DBの禁止領域で検索0件を期待する。
- 確率・競合caseは少なくとも100回反復と一意seed再現を行い、失敗回のseed/event IDを保存する。
- 合格はassertion数0ではなく、対象分岐・上下限・異常codeの要求coverage 100%をmatrixで証明する。

## 4. PT詳細観点

### 4.1 PT-CODEC（SS 322・323）

| ID群 | 必須観点 | 期待 |
|---|---|---|
| PT-CODEC-H-* | 256 byte header全field、offset、ASCII/N/X、protocol/layout/result、UUID、count/length | 全byte一致、未定義/gap/overlap/total不一致は恒久error |
| PT-CODEC-L-* | 64 layoutそれぞれmin/max、0/1/max record、`256 + data + record × count` | UI 233～236の宣言長と完全一致 |
| PT-CODEC-S-* | NFC前/後、日本語・surrogate・combining mark、byte上限-1/上限/上限+1 | Code-point境界でpadding、切断・暗黙truncateなし |
| PT-CODEC-P-* | Space/zero padding、sign/decimal禁止、control/NUL、invalid UTF-8、unknown enum | Decode/encode双方で一意error step/code |
| PT-CODEC-E-* | Error response filler、record count 0、body不足/過剰、上限1,000,000 byte | Result-code profileに従い、不正bodyはDLQ/process exit引継ぎ |

Golden vectorはlayout IDごとにencode完成byteのSHA-256、field境界hex、decode recordを保存する。

### 4.2 PT-AUTH（SS 314・352）

- Username NFC/trim/lowercase key、Login password 0/1/256/257 byte、作成password 11/12/128/129文字、Argon2id parameter/rehash、存在/不存在timingの統計的差。
- USER 4/5失敗、IP 9/10失敗、15分直前/到達/直後、成功clear、disable/lock/reset、同時Login race。
- Session 1/2/3件、最古revoke、idle 8時間直前/到達、restart、fixation、cookie hash、ciphertext/tag/AAD/key version改ざん。
- CSRF欠落/不一致/別session/再利用、SavedRequestのsafe GETとexternal/POST拒否、Logout POST、cache/header。
- USER/ADMINの全route/layout、owner/他人/不存在の404/403使い分け、Web/API二重検証、Web業務schema grant 0。

### 4.3 PT-IDEM・STATE（SS 312・324・332）

| 入力 | 期待 |
|---|---|
| 同Message ID・同body | 保存済response replay、業務更新0、`0200` |
| 同Message ID・異body/layout/owner | Protocol/security conflict、更新0、警告証跡 |
| 異Message ID・同token・同fingerprint | 同owner/operation/targetの保存済結果、更新0 |
| 異Message ID・同token・異payload | HMAC不一致`0105`、更新0、SECURITY log |
| Current/previous/unknown HMAC key | Current/previousは許可期間だけ一致、unknownはdeny closed |
| RECEIVEDの取消vs開始 | CASで1方だけ成功、CANCELLED後処理なし、PROCESSING後取消`0107` |
| 論理削除vs再読込・通知 | Ownerから即時非表示、FKは残り、期限/状態前の物理削除なし |

### 4.4 PT-DB・SQL（SS 331・332）

- 全PK/FK/UK/CK/NOT NULL、DEFERRABLEの有無、ON DELETE RESTRICT、複合game FK、partial index predicateをcatalog自動照合。
- N12/N9の0/上限/上限+1、UTF-8 byte上限、timestamptz境界、logical delete/version、sequenceのmigration後値。
- 検索条件の単独/AND/escape、大小文字、sort tie、0/-1/1/最終/超過page、0/50/100/101件。
- Query IDごとのindex利用候補、statement timeout、N+1不発生、ADMIN/USER/technical/migration roleの正負grant。
- Optimistic version 2更新、`FOR UPDATE SKIP LOCKED`複数dispatcher、deadlock/timeout/connection切断のrollbackとretry範囲。

### 4.5 PT-FILE・RANGE（SS 333）

- Empty/absolute/`..`/separator違い/NUL/Unicode欺瞞・各segment symlink・root symlink・hard link・open前後差替えを拒否する。
- Descriptorのsize/hash/MIME/suffix/owner/layoutを1項目ずつ改ざん、`.part`、欠落、短い/過剰file、atomic rename失敗。
- Scenario 200/201/10,000/10,001 recordと48,000,000 byte、transfer 5GB/5,000/9,000件境界、朝削除cutoff。
- Rangeなし、`0-0`、`0-1048575`、1MiB超、open-ended、suffix 1/total/total+1、複数・不正・overflow、416と`bytes */total`。
- Inline/downloadのMIME/Content-Disposition UTF-8、HEAD、If-Range非対応の扱い、owner違反の非存在同一応答。

### 4.6 PT-BATCH・OPS（SS 341～343）

- 05:00起動のstep全分岐、lock二重起動、root/symlink/mount/owner/mode不正、中止時点でのresume。
- PostgreSQL dump/list/restore/hashの成否、新規directory atomic publish、7/8世代、同日再実行、backup失敗時の業務cleanup skip。
- 保持cutoff直前/同値/直後、PENDING/PROCESSING/DLQ/security hold、chunk commit前後kill、FK RESTRICT、個別warning継続。
- Config allowlist/unknown key、environment差分、credential permission/symlink、release/config/schema/protocol/hash driftの起動拒否。

### 4.7 PT-LOG・SECURITY（SS 351・352）

- Action/error/result/metric label catalogの全値とunknown拒否、field byte上限、CRLF/control、JSON encode、UTC。
- Password/hash/context/cookie/CSRF/HMAC/AES key・nonce、質問/回答、fixed body、absolute pathのcanaryが全証跡で0件。
- Metric labelがusername/ID/request数で増加しないこと、warning/critical直前/到達/回復とopen/count/close。
- CSP/CSRF/header/XSS/SQL/CRLF/path/MQ ACL/DB grant/secret permissionの正負test、DEBUGでもredaction同一。

## 5. IT詳細観点

### 5.1 IT-E2E・INTERFACE

1. 64 layout全てをWeb→Artemis→API→DB/file→replyの実BytesMessageで最低1回通す。Request/replyの
   transport/business/correlation ID、wire byte長、DB後条件、画面表示、log相関を同一証跡にする。
2. Login/Logout、Scenario、Animation/Music、Log、User、質問/通知/取消/回答・削除をUSER/ADMINで通す。
3. Web REQUEST JSON→technical outbox→WLGEVT01→`app_logs`をBroker/API停止跨ぎで再送し、source Message IDの欠落/重複0。

### 5.2 IT-CRASH・RETRY

| Failpoint | 必須後条件 |
|---|---|
| Request receive前/後、DB commit前 | JMS rollback/redelivery、業務更新0 |
| DB commit後・reply send前 | Inboxによる再受信replay、業務更新1 |
| Reply send後・JMS commit前 | Transaction rollback後replay、Webは相関1結果 |
| Outbox claim/send/JMS confirm/mark-sentの各間 | 未送信の取りこぼし0、duplicateはInbox/broker cacheで1結果 |
| Async state RECEIVED→PROCESSING、answer/notification/outboxの各間 | FIFO、state/answer/notification/DLQが説明可能な一意状態 |
| Reply遅延がWeb 2秒timeout後 | 別requestへ取違え0、late reply ACK/metric、token再操作で結果回復 |

Broker/API/Web/PostgreSQLの単体・組合せ停止、Broker reboot、API restart rate limit、network loopback遮断、disk fullを
故障注入する。Artemis File Journalの通常crash recovery、破損検知、Queue件数回復を証跡化する。

### 5.3 IT-ASYNC・DLQ

- Consumerを必ず1とし、同時投入順/FIFO、処理中の後続停止、business timeoutなし、空回答STUBを確認する。
- Temporary errorは初回＋3再配送。第1=1秒、第2=5秒、第3はQA-041の承認値をtest profileの一意値にする。
  回答前は`PENDING_QA_041`とし、25秒または30秒を無断で合格oracleにしない。
- 恒久protocol errorは初回でDLQ・ACK・nonzero exit、DB不能の最終再配送はDLQとjob整合runbookを実行する。
- DLQ/Expiryのbody非表示、browse権限、個別replay、同Message ID Inbox replay、自動purgeなしを確認する。

### 5.4 IT-OPS・RESTORE・SECURITY

- Morning依存順、stop timeout、systemdの10分5回rate limit、Caddy 55160だけpublic、loopback portの非公開。
- Backup復元を隔離DB→新instanceの順で実行し、schema/role/constraint/count/Queue整合、RPO/RTO 24時間を測定。
- Asset master 59,627 file/19,240,707,190 byte、Scenario 262/99,661、audio 37,256、link 35,201、video 20、music 129をhash/count検証。
- USERからADMIN/他人、直接Queue/DB/file/port、credentialのargv/env/log、CSP/CSRF/session改ざんを攻撃testする。
- DEBUG→STANDARD切替で詳細metric componentを停止しても、systemd/journal/DB/Artemis/disk/最小healthが継続する。

### 5.5 IT-PERFORMANCE・CAPACITY

| 負荷 | 判定 |
|---|---|
| STANDARD、同時10名×1同期request | End-to-end p95 <=2.5s、MQ待ち<=2.0s、取違え0、timeout/error率併記 |
| Search worst、Log 100、新規一覧50、Scenario 10,000 | Query ID・plan・pool・heap・wire/file上限内 |
| 20 media stream/Range 1MiB | 同時数上限、Range開始、FD/thread/direct memory、他画面p95への影響 |
| Async/Web log Queue 70/90%、transfer 3.5/4.5GB | Warning/critical、新規受付9001、既受付・証跡を失わない |
| 16GB memory・256GB disk budget | Systemd MemoryMax、PG/Artemis/JVM/direct/journal/paging/backup合計が上限内 |

## 6. Test data・fixture

- `PT-BASE`: USER 3、ADMIN 2（active/self保護を含む）、各stateのQuestion/Job/Notification/Answer、各game/media。
- `PT-BOUNDARY`: 各fieldの0/1/max-1/max/max+1 byte、NFC/NFD、禁止control、同sort key、存在/欠落file。
- `IT-CURRENT-MASTER`: 264に固定したcurrent masterのread-only copy/manifest。原本を書き換えない。
- `IT-FAULT`: failpoint、Queue/disk/clock制御、ダミーcredential。Production credentialを試験に使わない。

Password・key・contextはGit管理しない。Fixture生成seed、schema/protocol/config version、master manifest hashはGitと
reportに固定する。

## 7. 証跡・合否・不具合分類

| 証跡 | 内容 |
|---|---|
| Machine report | JUnit XML/HTML、case ID、duration、seed、environment/release/config/schema/protocol |
| Interface | HTTP header/body hash、wire SHA-256/byte length、JMS propertyのredacted dump |
| Persistence | SQL assertion/query ID、constraint/index/lock、Queue/DLQ/Expiry count、file manifest/hash |
| Operation | systemd/journal/metric/alert、backup/restore manifest、failpoint timeline |
| Trace | RD→UI→SS→test ID、requirement coverage、未実施/除外理由・承認 |

Failed/flaky/skipped/not-runは合格に算入しない。不具合は(a) PG実装不具合、(b) SS設計不備、
(c) UI修正必要、(d) RD修正必要、(e) environment/toolingに分類する。(c)/(d)は対応台帳へ先に登録し、
上位期待値をtestに合わせて無断更新しない。

## 8. Entry/exit gate

PT開始は対象class/migration/configとreview、関連SS/test case、fixture、実環境の準備完了を条件とする。
IT開始はPT必須case合格、同一release artifact、全componentのconfig/credential、障害注入・rollback手順を条件とする。

PT/IT完了は必須caseのfailed/flaky/skipped/not-run 0、重大不具合0、trace/coverage 100%、証跡のrelease commitひも付け、
機密漏えい0、resource/restore実測値の設定manifest反映とする。QA-041未解決中は再配送間隔caseを
`skipped`合格にせず、IT完了前に承認oracleへ固定する。

## 9. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-051 | DB/MQ/file依存のcomponent PTとITは実PostgreSQL/Artemis/file systemで合格判定 | T-001/T-004、dialect・lock・journal・pathの代替実装差を見逃さない | Test environment/container/OS fixture |
| SS-D-052 | Crash pointを名前付きfailpointでDB/JMS/outboxの境界ごとに試験 | 時間依存でなく再現し、処理結果を一意に検証 | PGのfailpointは試験build限定、IT証跡 |
| SS-D-053 | QA-041未回答の第3再配送間隔をparameterized pending oracleとし、いずれも仮合格しない | UI正本を無断変更せず、その他の試験設計を完了可能にする | QA回答後321/342/354/test dataを同時更新 |

## 10. 禁止事項

- H2/in-memory mockだけでPostgreSQL/Artemis/file結合を合格、flaky/skippedをretry成功で隠蔽。
- Productionの認可、CSRF、暗号、constraint、redaction、durabilityをtest profileで無効化。
- DB/Queue/fileをcase後条件確認なしに一括purgeし、二重更新・DLQ・取違いを検出不能にする。
- 実測が上位仕様と異なる際にoracle/設定だけを書き換え、QA/RDF/UIC/変更管理を省略。

## 11. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | PT/ITの分岐・境界・異常・競合・再送・性能・復旧と証跡/gateを詳細化。 |
