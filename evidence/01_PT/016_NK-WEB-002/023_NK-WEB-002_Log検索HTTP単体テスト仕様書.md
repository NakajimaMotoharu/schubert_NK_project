# Log検索HTTP単体テスト仕様書

Program NK-WEB-002 / SCR-014。対象 `LogController.search`、`LogMvcConfiguration.logController`、実`logs.html`、`LogSearchWireClient`。RD FUN-008/AUT-002/MON-003/TST、UI221/222/225/232/235、SS311/313/314/323/351/352、SSC-048/073、PG-D-218。2026-09-23仕様先行。結果・coverage・commitは未実行につき未認定。対応結果は024、正式証跡は本Programの`evidence/manifest.json`。

| Test ID | 目的・入力/操作 | 独立期待値 |
|---|---|---|
| PT-SCR-093 | ADMIN、空/全条件、0000/0200、0/1/100件 | GET `/logs`200、LGSREQ01一電文、UI232/235の固定offset/lengthに手組golden、actor contextのみ、100件/page、独立DOM行/日時/順序 |
| PT-SCR-094 | unknown/duplicate/byte超過/enum/date/page不正 | 同一画面400・field error/結果なし、LGS送信0。server拒否はJS無効でも成立 |
| PT-SCR-095 | 0100/0101/0103/0104/0105/0106/0107/9000/9001 | SS351の固定HTTP status、後続送信0、秘密・raw provider causeを画面へ出さない |
| PT-SCR-096 | 0102の通常GET | local session/snapshot破棄、302 `/login?session-expired`、古いcookie再利用不可、追加MQなし |
| PT-SCR-097 | 不正header/record/transportとresponse不整合 | 固定503、Model/result描画なし。UI232 byteとSS313投影invariantの独立反例 |
| PT-SCR-098 | null引数/異種Principal/未知例外・response write故障 | null契約と固定SessionStoreException、未知Errorは握りつぶさず、IOException identityを維持 |
| PT-SCR-099 | MVC GET/HEAD/POST、重複field | GET/HEAD200・POST405、HEAD実bodyなし、重複400・MQなし、固定template名 |
| PT-SCR-100 | 実HTTP匿名/USER/ADMIN Login | 匿名302、USER403（LGS0）、ADMIN200＋role/session再検証、`Cache-Control:no-store`、CSRF表示はLogoutだけ |
| PT-SCR-101 | 64並行ADMIN request・異なるcontext/filter | 64独立correlation/context/表示。共有Model・条件混線0 |
| PT-SCR-102 | HTML注入、row optional、0/101件 | escaped DOM、詳細折畳み・ページ条件保持、0件固定文言。UI225・Current DOMとの明示比較 |
| PT-SCR-103 | public script GET/HEAD/POST・未知資源 | GET/HEADのみ配信、POST・未知拒否。inline JS・token埋込なし |
| PT-SCR-104 | CHR-L01実NK adapter | Current baseline保護、DIF-002/008/010/015以外差分0。fixture PTとは別run/結果で証跡化 |

fixtureは独立したJMS同期返信、公開synthetic user/session・PG test schema・loopback HTTP。正常/境界/異常/例外/null/並行/再送を上表と既存PT-WEB270～285/PT-SCR084～092へ分配し、既存部品の合格を重複加算しない。`LogSearchViewModel`のsuccess invariantも応答byteと独立件数/順序で検査する。期待値はProduction encoder/view mapperで作らず、UI232/235の固定byte位置、明示status/DOM、Current baselineの固定caseを使う。正式実行commandは451の`clean verify`と018全scope収集/validate、影響CHR-L01は実NK adapterから独立実行。Java4coverage・JS3coverage各100%、静的解析0、failed/flaky/skipped/not-run0。実行日時/branch/commit/OS/JDK/Maven/Node、終了code、redacted input/expected/actual、関連BUG/SSC、証跡path/hashは024とmanifestへ記載する。
