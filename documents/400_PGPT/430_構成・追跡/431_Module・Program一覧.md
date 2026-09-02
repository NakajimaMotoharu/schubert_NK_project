# Module・Program一覧

## 1. 管理規則

Program IDは`NK-<領域>-NNN`、Test IDはSS 354の既存群（`PT-CODEC-*`、`PT-AUTH-*`等）をprefixとしてProgram内で欠番なく採番する。Class/method、resource、DDL、設定、test、evidenceをProgram IDで束ね、RD要件ID・UI文書・SS文書へforward/reverse traceする。正式module名はSS 311を正とする。

## 2. Module一覧

| Module | Production path | 責務 | 許可依存 | 主SS |
|---|---|---|---|---|
| `schubert-nk-protocol` | `src/schubert-nk-protocol` | 256-byte header、64 layout、value object、codec、error | JDK/JSpecifyのみ | 311、322、323 |
| `schubert-nk-api` | `src/schubert-nk-api` | JMS consumer、業務service、DB/file、Inbox/Outbox | protocol | 311、312、321、324、331～333 |
| `schubert-nk-web` | `src/schubert-nk-web` | Login/session/CSRF、controller/form/template、JMS client、Range | protocol | 311～314、321、333 |
| `schubert-nk-batch` | `src/schubert-nk-batch` | 朝batch、backup、削除、再実行 | 原則JDK、限定protocol | 311、341 |
| deployment/migration | `src/deployment`、`src/migration` | Caddy/systemd/PostgreSQL/Artemis/Java設定、移行・切戻し | Artifact公開契約 | 331、342、343、351～353 |
| NK Characterization adapter | `program/characterization` | Current baselineを変更しないNK比較 | Production HTTP公開契約 | 355 |

## 3. Program一覧

| No. / Program ID | Module・主class/resource | 関連RD | 関連UI | 関連SS | PT directory | CHR | 状態 |
|---|---|---|---|---|---|---|---|
| 001 / `NK-PRO-001` | Header/field/value/catalog | MQ-014～038、MSG-001～011 | 232～236 | 311、322～323 | `001_NK-PRO-001` | A/S/M/L/E/N | PG/PT中（中間gate 17件PASS、389 field catalog・69 named record・64明示mapper完了。semantic wrapper未実装） |
| 002 / `NK-PRO-002` | FixedWidthEncoder/Decoder、64 payload | MQ-014～045、MSG/MSG-F | 233～236 | 322～324 | `002_NK-PRO-002` | A/S/M/L/N | PG/PT中（中間gate 24件PASS、64 layout field/error codec・named mapper完了。semantic/cross-field/golden未実施） |
| 003 / `NK-PRO-003` | Large-result codec、JST timestamp、descriptor validation | MQ-035/039～041、FIL-001～009 | 232、237 | 322～323、333 | `003_NK-PRO-003` | S/M/O | PG/PT完了（12/12、coverage全100%、SpotBugs 0） |
| 004 / `NK-DAT-001` | Flyway V001～V005、21 table、index/constraint/role/grant | DAT-001～011、BAK/MIG-DAT | 241～242、251、254 | 331～332、343 | `004_NK-DAT-001` | A/S/M/L/N/O | 未着手 |
| 005 / `NK-MSG-001` | Artemis設定、JMS request/reply/correlation | MQ-001～013/040～045 | 212～213、231 | 312、321 | `005_NK-MSG-001` | A/S/M/L/E/O | 未着手 |
| 006 / `NK-MSG-002` | Inbox/Outbox/replay/retry/log outbox | ASY-001～009、MQ-006～010 | 213、231～236、241 | 312、324、332 | `006_NK-MSG-002` | L/N/O | 未着手 |
| 007 / `NK-AUT-001` | Authentication/attempt/session/context/owner/role | FUN-001/009、AUT-001～004 | 225～226、234、241 | 312、314、331～332 | `007_NK-AUT-001` | A01～A03/U02/O01 | 未着手 |
| 008 / `NK-SCN-001` | Scenario/game/speaker/route/file/detail query | FUN-003～005 | 223～224、234 | 312～313、323、332 | `008_NK-SCN-001` | S01～S08 | 未着手 |
| 009 / `NK-MED-001` | Audio/animation/music descriptor/query/file/Range | FUN-005～007、FIL/PER | 223、235、237 | 312～313、323、333 | `009_NK-MED-001` | M01～M07 | 未着手 |
| 010 / `NK-ADM-001` | User query/create/status/role/password/unlock | FUN-009、AUT-001～003 | 225、236、242 | 312～314、323、332 | `010_NK-ADM-001` | N01 | 未着手 |
| 011 / `NK-QST-001` | Question submit/token/HMAC/receipt | FUN-010/101～107、QST-001～004 | 224、236 | 312～314、324、332 | `011_NK-QST-001` | N01 | 未着手 |
| 012 / `NK-ASY-001` | FIFO worker、empty AnswerProvider、state/error/DLQ | ASY-001～009、QST-101～105 | 213、231、236 | 312、321、324、332 | `012_NK-ASY-001` | N01/O01 | 未着手 |
| 013 / `NK-NTF-001` | Notification list/detail/cancel/owner/race | FUN-011、NTF-001～012 | 224、236、242 | 312～314、323～324、332 | `013_NK-NTF-001` | N01 | 未着手 |
| 014 / `NK-QRY-001` | Question/answer search/detail/logical delete | FUN-012～013、QST-005～010、DAT-009～011 | 224、236、242 | 312～314、323～324、332 | `014_NK-QRY-001` | N01 | 未着手 |
| 015 / `NK-WEB-001` | Security/session/JMS/form/mapper/error/common layout | SYS-006～007、FUN-001～013、TST | 221～226 | 311～314、321、351～352 | `015_NK-WEB-001` | A/U/E/O | 未着手 |
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
