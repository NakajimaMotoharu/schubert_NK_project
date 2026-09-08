# NK-DAT-001 認証Inbox参照単体テスト仕様書

## 1. 対象・契約

Program NK-DAT-001/NK-AUT-001、`AuthenticationInboxInspector` constructor/isConsistent。RD OPS-009/AUT-001/004/MQ-008、UI212/232/234/241/251、SS324 §6.1/6.2/12.2、SS331/352、QA-046/UIC-006/SSC-049、PG-D-120、BUG-014/YKT-012。
構造検査だけでは足りないLogin/Logoutの保存参照をcaller-owned transactionで照合する。trueは参照整合だけで削除権限・認証成功ではない。SQL更新・commit/rollback/close・log/送信なし。異常はfalse、null呼出しは例外。他layoutはfalse。

## 2. 独立ケース

共通fixtureは専用一時PostgreSQL 18、synthetic user/session、runtime乱数鍵。入力wireはUI232/234のoffsetから手書きし、暗号は独立JCE AES-GCM、圧縮はDeflater3、AADはSS352のlength prefixを独立組立。expectedはliteral booleanと明示SQL後条件。Productionのcapture/encodeでexpectedを生成しない。鍵・context・暗号文はGit証跡へ保存しない。

| Test ID | method | 入力・操作・期待値 | 目的/根拠 |
|---|---|---|---|
| PT-DB-INBOX-009 | loginOriginalAndLaterAccountState | 正常成功、後日username/role/status/idle期限変更後ともtrue。session/context/監査の追加・更新0 | SS324 §6.1の初回値凍結 |
| PT-DB-INBOX-010 | logoutOwnerAndRevokedReference | 0000/0200、正しいowner/失効時刻true。owner/UUID/hash/時刻/未失効はfalse | §6.2。新たな失効なし |
| PT-DB-INBOX-011 | deterministicErrorReferences | LGN0101/0106、LOG0102はERROR/NONEでtrue。異code/ref/stateはfalse | 確定errorだけ保存 |
| PT-DB-INBOX-012 | missingAndInconsistentLoginRows | session欠落、Message/context/hash/key/issued不一致はfalse、SQL rollback後元行が不変 | immutable DB参照と暗号照合 |
| PT-DB-INBOX-013 | identityStructureAndNullContracts | 非対象layout、owner有無逆転、壊れたwire/metadataはfalse。constructor/args nullはNPE | nullを正常扱いしない |
| PT-DB-INBOX-014 | databaseFaultsAndTransactionOwnership | autocommit/SQL fault/close済接続false、caller connection生存、commit/rollbackを呼ばない | 基盤故障と非更新 |
| PT-DB-INBOX-015 | keyRotationAndClosedLifetimes | current/previous鍵true、unknown/wrong/closed鍵false、途中close false | fail closed、秘密情報非公開 |
| PT-DB-INBOX-016 | concurrentReferencesDoNotCross | 100並行で正常/不正refの結果が混ざらず、DB/入力buffer不変 | private codec排他と参照非更新 |

## 3. 実行・判定

JDK25.0.4、Maven3.9.12、JDBC42.7.13/Flyway13.4.0、Junit5.13.4、JaCoCo0.8.15、SpotBugs4.10.4.0/NullAway。正式はrepoで `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress clean verify`。
追加classのline/method/class/branch各100%、失敗/skip/flaky0、全回帰成功と参照/hash整合を要求する。実行日時/commit/command/exit/coverage/エビデンスpath/hashは006結果と専用manifestへ確定後記録する。現時点NOT RUN。SQL削除/lock/権限/oneshotと非認証layoutは本試験の合格に含めない。
