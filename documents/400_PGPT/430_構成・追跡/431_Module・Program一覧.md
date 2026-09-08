# Module・Program一覧

最新確定: 正式PT-ADM-20260908-13、source 945d310e0ea88952a44a4a18f7261df392846858、dev-admin、2026-09-08 18:59:32～19:03:44 JST。全625件（Protocol80/Storage34/API394/Web76/CHR41）、failed/error/skipped0、5対象moduleのline/method/class/branch全100%、NullAway/Enforcer/format PASS、SpotBugs0。Admin73、Inbox11+3+4、Media61、Scenario155/Auth91等は重複する内数。Log read-only→現在認証/ADMIN→Inbox/critical監査・独立wire/DB-HMAC・完了24h・100並行・実JMS再送7件を追加PASS。再送監査は新検索へ表示されるが元結果へ混入しない。新規障害なし。Web session/security（PG-D-093/PT-WEB-001～008先行仕様）、HTTP/全layout登録/起動/実NK CHR、QA-045承認依存は継続。確定Program5/20=25%（件数比、工数換算なし）、明確な行き詰まり0件。以下は履歴。

最新確定: 正式PT-ADM-20260908-04、source 1f1d321ad40bd7ba5f8461e5954e94e7ac6142d3、dev-admin、2026-09-08 15:59:29～16:03:00 JST。全571件（Protocol80/Storage34/API340/Web76/CHR41）、failed/error/skipped0、5対象moduleのline/method/class/branch全100%、NullAway/Enforcer/format PASS、SpotBugs0。Admin23、Media61、Scenario151/Auth91等は重複する内数。User作成/状態/role/password/unlock、実PG監査・全session失効・故障rollback・独立PBKDF2/USRMUT24・並行raceを追加PASS。BUG-045～047/YKT-040～042は再試験完了。正式03は静的解析失敗で非合格。SSC-031の外側Inbox接続とSSC-032の新規canonical接続、HTTP/起動/実NK CHR、QA-045承認依存は継続。確定Program5/20=25%（件数比、工数換算なし）、明確な行き詰まり0件。以下は履歴。

最新確定: 正式PT-ADM-20260908-02、source c828f77ec11b1b0727724050323700c19b04dc76、dev-admin、2026-09-08 15:13:34～15:16:56 JST。全561件（Protocol80/Storage34/API330/Web76/CHR41）、failed/error/skipped0、5対象moduleのline/method/class/branch全100%、NullAway/Enforcer/format PASS、SpotBugs0。Admin13、Media61、Scenario151/Auth91等は重複する内数。SSC-031の管理認証prelude・実相互target/role再検証/100並行・全faultを追加PASS。SSC-031はUser command/Inbox接続まで対応中。確定Program5/20=25%（件数比、工数換算なし）、明確な行き詰まり0件。User更新本体・HTTP/起動/実NK CHRと未完了Program、QA-045承認依存は継続。以下は履歴。

最新確定: 正式PT-ADM-20260908-01、source 9cbdfa1ae9dfda67557f48405c55a6a019294b71、dev-admin、2026-09-08 14:58:00～15:01:23 JST。全555件（Protocol80/Storage34/API324/Web76/CHR41）、failed/error/skipped0、5対象moduleのline/method/class/branch全100%、NullAway/Enforcer/format PASS、SpotBugs0。Admin照会7、Media61、Scenario151/Auth85等は重複する内数。User一覧/詳細・独立wire/実PG権限/NULL/時刻/容量・close/100並行をPASS。User更新接続前にSSC-031の認証/target lock順を先行補足し、PT-ADM-008～013は未実施。確定Program5/20=25%（件数比、工数換算なし）、明確な行き詰まり0件。HTTP/起動/実NK CHRと各未完了Program、QA-045承認依存は継続。以下は履歴。

最新確定: 正式PT-MED-20260908-11、source 34ba78f138fd1e1db0cca48501f9b787ff4c526e、dev-media、2026-09-08（開始終了日時はmanifest）。全548件（Protocol80/Storage34/API317/Web76/CHR41）、failed/error/skipped0、5対象module全line/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。Media61件（他Programと重複する内数）。8queryの認証/Inbox→DB外の実file→最新認証/確定→実JMS送信・ACK、100同一Message再送と障害回復を追加PASS。BUG-044/YKT-039の時刻oracle再試験完了。Web session/security・HTTP/画面/起動登録/実NK CHRは残件。確定5/20=25%（Program件数比、工数換算なし）、明確な行き詰まり0件。SS362順でUser管理APIのPG/PTへ進む。以下は履歴。

最新確定: 正式PT-MED-20260908-10、source 9b152e0797948d1f346855bf5441164a46804618、dev-media、2026-09-08 13:58:53～14:01:59 JST。全541件（Protocol80/Storage34/API310/Web76/CHR41）、failed/error/skipped0、5対象module全line/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。Media54件（他Programと重複する内数）。全8応答snapshot/独立JCEと手組wire/改変拒否/100並行を追加PASS、BUG-043/YKT-038のBerror oracle是正・再試験完了。実認証Inbox/file/JMS段階接続・HTTP/起動/実NK CHRは継続。確定5/20=25%（件数比、工数換算なし）、明確な行き詰まり0件。詳細manifest、以下は履歴。

最新確定: 正式PT-MED-20260908-09、source c5de0e44d433180680c0c87b1c32612d7b37060e、dev-media、2026-09-08 13:43:18～13:46:23 JST。全536件（Protocol80/Storage34/API305/Web76/CHR41）、failed/error/skipped0、5対象module全line/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。Media49件、Scenario151等は重複する内数。checksum manifest/実保持asset metadata・59,627合成件数・異常/100並行を追加PASS、BUG-042/YKT-037再試験完了。認証Inbox/応答snapshot/実HTTP・起動/実NK CHRは継続。確定5/20=25%（件数比、工数換算なし）、明確な行き詰まり0件。詳細manifest、以下は履歴。

最新確定: 正式PT-MED-20260908-02、source dc580fc7ed9c9f608430072b1ddf5caaf646eaae、dev-media、2026-09-08 12:14:50～12:17:52 JST。全501件（Protocol80/Storage26/API289/Web65/CHR41）、failed/error/skipped0、5対象module全line/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。 Media14件（先行Range/header/stream7＋実PG menu/list7）成功。各Programの内数を重複加算しない。descriptor/manifest/認証・実asset/20permit/HTTP/起動/実NK CHR等は未完了、確定5/20=25%を維持。詳細manifest/Test ID/hash、以下は履歴。

最新確定: 正式PT-MED-20260908-01、source d986d3e3163069522fa052491a7431f865d673f7、dev-media、2026-09-08 11:59:40～12:02:43 JST。全494件（Protocol80/Storage26/API282/Web65/CHR41）、failed/error/skipped0、全5moduleのline/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。 Media7/Scenario143/Auth85/Inbox11+3/PRO00317は重複する内数。Media Range/header/bounded stream部品PASS、API query/descriptor/認証・asset/manifest・20permit/HTTP/実NK CHR等は未完了。確定Programは5/20=25%（件数比、工数換算なし）。詳細は対応manifest/Test ID/hash、以下は履歴。

最新確定: 正式PT-SCN-20260908-23、source e6b4368407043850f0d11a8227d5577977f4868c、2026-09-08 11:46:25～11:49:26 JST、全487件（Protocol80/Storage26/API282/Web58/CHR41）。failed/error/skipped0、5対象module全line/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。 Scenario143/Auth85/coordinator11/置換3/PRO00317は重複する内数であり全体へ加算しない。確定5/20=25%、SSC-023/024の段階接続を確認。SSC-027の内部serviceはPASS、本番起動/登録は別残件。 以下は履歴。

2026-09-08 11:46 暫定判定: BUG-040/YKT-036のstorage拡張子検証漏れを修正前起票し、NK-PRO-003完了を再試験まで保留。確定4/20（20%、工数換算ではない）。正式22は全486件/coverage100%/静的解析0だったが、collectorのTest ID完全名誤りBUG-041で収集未完了。以下の過去完了表示を現在判定としない。BUG-038/039の再試験と併せ、source/collectorを固定した正式23へ進む。

最新: 正式`PT-SCN-20260908-20`、source `e9d89e5a339320cc57dd7f50b9bb40810edd2a43`、dev-scenario、2026-09-08 11:02:42～11:05:27 JST。全479件（Protocol79/Storage26/API275/Web58/CHR41）、Scenario関連136/Auth85/coordinator11/置換3（重複を全体総数へ再加算しない）。failed/error/skipped0、5対象module全coverage100%、NullAway/Enforcer/format PASS、SpotBugs0。 NK-MSG-002のPT-IDEM-SR01～SR03でrow lock・旧暗号一致・2列限定置換/他17列不変を確認。NK-SCN-001の最終段階serviceを次に接続する。確定5/20=25%、Program残件とQA-045承認依存は継続。

## 1. 管理規則

Program IDは`NK-<領域>-NNN`、Test IDはSS 354の既存群（`PT-CODEC-*`、`PT-AUTH-*`等）をprefixとしてProgram内で欠番なく採番する。Class/method、resource、DDL、設定、test、evidenceをProgram IDで束ね、RD要件ID・UI文書・SS文書へforward/reverse traceする。正式module名はSS 311を正とする。

## 2. Module一覧

| Module | Production path | 責務 | 許可依存 | 主SS |
|---|---|---|---|---|
| `schubert-nk-storage` | `src/schubert-nk-storage` | SSC-021: 保持directory/inode、Linux native、OS属性/root配置。既存NK-SCN-001の低位能力を抽出（Program母数不変） | JDK/JSpecifyのみ、Protocol/業務module依存なし | 311、333、342、343 |
| `schubert-nk-protocol` | `src/schubert-nk-protocol` | 256-byte header、64 layout、value object、codec、error | JDK/JSpecifyのみ | 311、322、323 |
| `schubert-nk-api` | `src/schubert-nk-api` | JMS consumer、業務service、DB/file、Inbox/Outbox | protocol、storage（file adapterのみ） | 311、312、321、324、331～333 |
| `schubert-nk-web` | `src/schubert-nk-web` | Login/session/CSRF、controller/form/template、JMS client、Range | protocol、storage（file adapterのみ） | 311～314、321、333 |
| `schubert-nk-batch` | `src/schubert-nk-batch` | 朝batch、backup、削除、再実行 | 原則JDK、限定protocol | 311、341 |
| deployment/migration | `src/deployment`、`src/migration` | Caddy/systemd/PostgreSQL/Artemis/Java設定、移行・切戻し | Artifact公開契約 | 331、342、343、351～353 |
| NK Characterization adapter | `program/characterization` | Current baselineを変更しないNK比較 | Production HTTP公開契約 | 355 |

## 3. Program一覧

| No. / Program ID | Module・主class/resource | 関連RD | 関連UI | 関連SS | PT directory | CHR | 状態 |
|---|---|---|---|---|---|---|---|
| 001 / `NK-PRO-001` | Header/field/value/catalog | MQ-014～038、MSG-001～011、MSG-F02/F03、FIL-006 | 232～237、243 | 311、322～323、333 | `001_NK-PRO-001` | A/S/M/L/E/N | PG/PT完了（25/25、389 field・69 named record・64明示mapper・SS 323共通Java型、coverage全100%、SpotBugs 0） |
| 002 / `NK-PRO-002` | FixedWidthEncoder/Decoder、64 payload | MQ-014～045、MSG/MSG-F | 233～236 | 322～324 | `002_NK-PRO-002` | A/S/M/L/N | PG/PT完了（BUG-023/SSC-012の再試験で復帰。Run PT-AUT-20260908-06全317件/Protocol72、独立Login error3 PT・31response全error matrix、全coverage100%、SpotBugs0） |
| 003 / `NK-PRO-003` | Large-result codec、JST timestamp、descriptor validation | MQ-035/039～041、FIL-001～009 | 232、237 | 322～323、333 | `003_NK-PRO-003` | S/M/O | PG/PT完了（BUG-037/YKT-033再試験復帰、PT-SCN-20260908-23全487件/Program17/Protocol80、全coverage100%・静的解析0。32byte constant-time照合・32位置改変拒否） |
| 004 / `NK-DAT-001` | Flyway V001～V007、21 table、index/constraint/role/grant | DAT-001～011、BAK/MIG-DAT | 241～242、251、254 | 331～332、343 | `004_NK-DAT-001` | A/S/M/L/N/O | 完了判定再確認中（15 PTとV006 cleanup再試験は成功しBUG-015は完了。BUG-014 Inbox保護/YKT-012は未完了。従来完了から一旦除外） |
| 005 / `NK-MSG-001` | Artemis設定、JMS request/reply/correlation | MQ-001～013/040～045 | 212～213、231 | 312、321 | `005_NK-MSG-001` | A/S/M/L/E/O | **PG/PT完了**（`PT-JMS-20260904-01`。12/12 case、関連JUnit 65/65、全reactor 199/199 PASS。28 production class、instruction/branch/line/method各100%、SpotBugs/secret hit 0） |
| 006 / `NK-MSG-002` | Inbox/Outbox/replay/retry/log outbox | ASY-001～009、MQ-006～010 | 213、231～236、241 | 312、324、332 | `006_NK-MSG-002` | L/N/O | 実施中（PT-IDEM-001～009/011 PASS、010/012/013部分、014/015未実施。006証跡PT-AUT-20260908-13全349件/API188、全coverage100%、SpotBugs/NullAway0。API ingest、Outbox保持/NULL、format/Enforcer再生成まで試験済み。BUG-027 secret buffer消去・BUG-025完了起点保持とreplay期限不変を確認。HTTP投影/Inbox保護/stress未完了、BUG-014継続・015完了） |
| 007 / `NK-AUT-001` | Authentication/attempt/session/context/owner/role | FUN-001/009、AUT-001～004 | 225～226、234、241 | 312、314、331～332 | `007_NK-AUT-001` | A01～A03/U02/O01 | PG/PT実施中（PT-SCN-20260908-23全487件/Auth85。Login/Logout冪等/管理全失効/監査/rollback/競合/応答DATA mapper/暗号化Login replay/参照整合・不変 PASS。BUG-022～029/SSC-010～016直接対応完了、64byte表示/96byte比較key・V007・audit分離を確認。匿名Login Inbox/JDBC・実JMS再配送、owner付きLogout Inbox/100同時再配送、任意監査IP・stage時計進行はPASS。SSC-023のread-only認証事前確認（非更新/行lock非取得/100並行/失効再検証）PASS。全layout dispatcher・起動/管理command/expiry・Web recovery/HTTP/CHR接続は未完了） |
| 008 / `NK-SCN-001` | Scenario query/detail・API native directory | FUN-003～005、FIL-001～009 | 223～224、234、237 | 312～313、323、332～333、342 | `008_NK-SCN-001` | S01～S08 | PG/PT実施中（PT-SCN-20260908-23全487件/Scenario関連143成功、全coverage100%、静的解析0。5 query＋detailの独立byte/Current表示/前後/全voice/10000上限/NULL/SQL故障/100並行を確認。BUG-030～035、YKT-027/028/030/031、SSC-018完了。Native no-replace/100並行・保持FD寿命/差替え・BUG-036/YKT-032再試験PASS。保持inode・owner/group/mode/nlink/size・複合I/O故障はPASS。I/F応答投影と容量予約/100並行はPASS。Root論理非重複/保持属性・ext4/SDS検査は部品PASS。CREATE_NEW/属性設定/最大48MB write・hash/再試行/公開・清掃/100並行と容量の内部writer接続PASS。Web内部read-only readerの最大48MB/100並行・属性/hash二段検証・途中改変/リンク/close故障拒否PASS。起動前metadata scan・0byte part算入・複数dateを跨ぐ9000/10000/10001件境界・列挙/close/差替え故障拒否PASS。自作診断fileの起動probe（force/group/hash/no-replace/fsync/所有別清掃・不確定ready保全）PASS。SSC-026の6response保存/再送部品（独立byte/暗号・改変拒否・100並行）PASS。SSC-027 guard/実ready完全性・不在検査/元content再生成/descriptorだけの暗号置換は内部10追加PT PASS。T01～T07の段階認証/Inbox/実DB-file-JMS・100同時/原本再生成接続PASS。全root実体/exclusive起動結線/readiness・scan-to-service初期化・本番service登録・HTTP/実NK CHR未完了、SSC-017/019・YKT-029継続） |
| 009 / `NK-MED-001` | Audio/animation/music descriptor/query/file/Range | FUN-005～007、FIL/PER | 223、235、237 | 312～313、323、333 | `009_NK-MED-001` | PT-MED-001～061 | PG/PT実施中（正式PT-MED-20260908-11全548件/Media61・全coverage100%/静的解析0。8DB query/要求canonical、保持全segment・Web内部Range/HEAD/download/20permit、応答binding、manifest/file、暗号snapshot、段階認証Inbox・実DB/file/JMSの100同一再送/障害回復までPASS。Web session/security・HTTP/画面/起動登録/実NK CHRは継続） |
| 010 / `NK-ADM-001` | User query/create/status/role/password/unlock、管理Log query（PG-D-090） | FUN-008～009、AUT-001～003/MON | 225、235～236、242 | 312～314、323、332、351 | `010_NK-ADM-001` | PT-ADM-001～073 PASS | PG/PT実施中（正式PT-ADM-20260908-13全625件/Admin73、全coverage100%/静的解析0。User更新5layoutと照会2layoutの現在認証/ADMIN・Inbox/HMAC・監査/凍結再送・実JMS、Log query/request/replay/application19件・完了24h/実JMS PASS、SSC031～037完了。HTTP/全layout登録/起動/実NK CHR残件。Web画面はNK-WEB-002、Program数は不変） |
| 011 / `NK-QST-001` | Question submit/token/HMAC/receipt | FUN-010/101～107、QST-001～004 | 224、236 | 312～314、324、332 | `011_NK-QST-001` | N01 | 未着手 |
| 012 / `NK-ASY-001` | FIFO worker、empty AnswerProvider、state/error/DLQ | ASY-001～009、QST-101～105 | 213、231、236 | 312、321、324、332 | `012_NK-ASY-001` | N01/O01 | 未着手 |
| 013 / `NK-NTF-001` | Notification list/detail/cancel/owner/race | FUN-011、NTF-001～012 | 224、236、242 | 312～314、323～324、332 | `013_NK-NTF-001` | N01 | 未着手 |
| 014 / `NK-QRY-001` | Question/answer search/detail/logical delete | FUN-012～013、QST-005～010、DAT-009～011 | 224、236、242 | 312～314、323～324、332 | `014_NK-QRY-001` | N01 | 未着手 |
| 015 / `NK-WEB-001` | Security/session/JMS/form/mapper/error/common layout | SYS-006～007、FUN-001～013、TST | 221～226 | 311～314、321、351～352 | `015_NK-WEB-001` | PT-WEB-001～008先行仕様 | PG/PT着手準備（PG-D-093。session ID・safe SavedRequest境界から実装、Spring session/暗号/CSRF/HTTP等は未実施） |
| 016 / `NK-WEB-002` | 全controller/template/static asset | FUN-002～013、PER-002～004 | SCR-002～023/090 | 313～314 | `016_NK-WEB-002` | U/S/M/L/E/N | 未着手 |
| 017 / `NK-BAT-001` | Morning lock/backup/business/technical/transfer/expiry | OPS-009～017、BAK/BKO/AVL | 251～252 | 331、341～343、353 | `017_NK-BAT-001` | O01 | 未着手 |
| 018 / `NK-OPS-001` | Caddy/systemd/PostgreSQL/Artemis/Java/config/log/metric/security | SYS/ENV/PER/AVL/OPS/MON | 211～212、231、243、251～253 | 321、342～343、351～353 | `018_NK-OPS-001` | L/E/O | 未着手 |
| 019 / `NK-MIG-001` | Migration/manifest/initial data/cutover/cutback | MIG/MIG-DAT/FIL/SCM | 243、254 | 331、343、353 | `019_NK-MIG-001` | S/M/O | 未着手 |
| 020 / `NK-CHR-001` | Shared case runner、Current/NK adapter、semantic comparator、gate | SCP-004、TST-001～005 | 223、264 | 354～355 | `020_NK-CHR-001` | 全24 | PG/PT完了（41/41、coverage全100%） |

## 4. Trace gate

- RD全281要件のうち実装対象は少なくとも一つのProgram/Testへforward traceする。
- 全production class/method、DDL、設定、template、scriptはRD/UI/SS/Testへのreverse traceを持つ。
- Test IDは一つのPT仕様行、test method、実行結果、evidence manifest entryへ一意に対応する。
- Trace漏れが一件でもあればPG/PT完了としない。

## 5. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-09-01 | 4 production module、deployment/migration、Characterizationと20 Programを登録。 |
| 2026-09-02 | NK-CHR-001のPG/PT完了、BUG-001/YKT-001再試験・evidenceを反映。 |
| 2026-09-02 | Protocol基盤の中間gateとNK-PRO-003完了を反映。NK-PRO-001/002の未実装範囲を明記。 |
| 2026-09-02 | UI 234～236の389 field catalog、64 layout success/error field codec、BUG-003/YKT-003再試験を中間gateへ反映。 |
| 2026-09-02 | SS 323の69 named record、64件の明示mapper、独立class名fixtureを中間gateへ反映。 |
| 2026-09-02 | SS 323の日時/UUID/context/SHA/path semantic型、BUG-004/YKT-004再試験、Protocol 52 PTを中間gateへ反映。 |
| 2026-09-02 | SS 323のN12 ID、primitive数値、X numeric、全wire enumとconstructor invariantを完了し、NK-PRO-001をPG/PT完了。 |
| 2026-09-02 | SS 322 §8/§9のresult profile・layout相関、64 layout独立golden、最大record・並行性を完了し、NK-PRO-002をPG/PT完了。 |
| 2026-09-02 | NK-DAT-001の実PostgreSQL 18/Flywayを用いるPT-DB-001～015を仕様化し、PG/PT実施中へ更新。 |
| 2026-09-03 | NK-DAT-001のFlyway/DDL、Security hold、role/grant、6 maintenance functionの全guard/正常分岐、実DB証跡を確定しPG/PT完了。 |
| 2026-09-03 | NK-MSG-001/002のprogram別PT仕様を確定し、Artemis/JMSとInbox/OutboxのPG/PT並行実施を開始。 |
| 2026-09-03 | NK-MSG-001のbroker/JMS境界とWeb相関registryの中間gateを反映。未完了caseを明示しProgram完了判定は保留。 |
| 2026-09-03 | NK-MSG-001のWeb request/reply client、12並行wait・13件目拒否・全終了経路cleanupをPT-JMS-008へ反映。 |
| 2026-09-03 | NK-MSG-001の実ACL 90組合せ、全4 route/provider負値、DLQ/Expiry再起動保持、production request senderを反映。PT-JMSは11 PASS・1未実施。 |
| 2026-09-03 | NK-MSG-001のAPI Reply/DLQ sender、caller所有transactionのcommit/rollback実brokerPTを反映。API中間gateを52件へ更新。 |
| 2026-09-03 | NK-MSG-001のWeb reply decoder/consumer、active/late ACK、body/type不変DLQ隔離、隔離失敗rollbackを反映。Web中間gateを27件へ更新。 |
| 2026-09-04 | NK-MSG-001のAPI sync/work/log listenerを含む最終reactor runとPT-JMS-012 scanを完了。sanitized evidence/manifest/hashを固定し、ProgramをPG/PT完了へ更新。 |
| 2026-09-05 | NK-MSG-002の`JdbcInboxCoordinator`とrequest/completion/result model、PT-IDEM-004～006の実PostgreSQL transaction/replay/競合証跡を反映。PT-IDEM-001～008を中間PASSとし、未実施009～015を明示。 |
