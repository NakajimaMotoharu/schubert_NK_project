# NK-DAT-001 非認証Inbox参照検査単体テスト仕様書

## 1. 対象と独立oracle（実装前）

NonAuthenticationInboxInspector constructor/isConsistent/内部decode・SQL参照。RD OPS-009/MQ-008/DAT-009/FUN-003～009、UI212/234/235/236/237/241/251、SS324 §12.4/331/333/352、QA-046/UIC-006/SSC-049、PG-D-123、BUG-014/YKT-012。Production API maintenance、結果014。参照検査だけであり専用SQL権限・lock・削除・oneshot完了とは扱わない。

独立UI fixture layouts-ui233.tsv/fields-ui234-236.tsvのbyte長・offsetへ手組値を格納する。Production layout/encoder/captureを入力期待値生成に使わず、NKENC1も独立JCE+Deflaterで作る。保存可能codeの期待表はSS324 §12.4の明示値、DBはproduction DDL上の別SQL後条件、生成file hashはpublic synthetic値（実体比較の証拠ではない）。秘密/生context/wireを証跡へ出さない。

## 2. Test ID（未実施）

| Test ID / method | fixture・入力・操作 | 独立期待値 |
|---|---|---|
| PT-DB-INBOX-041 / querySuccessAndPersistentErrors | 22 layoutと全result、手組正常DATA/空record、ERROR profile | SSの保存可能code表のみ許可。queryはNONE、未保存0102/0103/9000等は保持 |
| PT-DB-INBOX-042 / userMutationReferencesAndVersions | CREATE/4更新/ULK0200、id/型/不存在、現在version 0/1/9/999999999、後続name/role/status変更 | 参照USER=id、CREATE保存0、他成功>=1、現在>=保存。後続変更を誤拒否しない |
| PT-DB-INBOX-043 / scenarioInlineAndFileReferences | SCN I/F、2game、descriptor日付/UUID/長さ/hash、参照type/id/game/欠落 | IはNONE、Fは整合したSCENARIO_FILEのみ。生成file実体なしでも参照検査可、raw master hash非比較 |
| PT-DB-INBOX-044 / identityCryptoAndNullContracts | 匿名/対象外/別AAD/欠落/破損/closed key、null3引数/constructor | 未検証false、呼出しnull明示拒否、鍵/平文を返さない |
| PT-DB-INBOX-045 / databaseFaultsAndNullRows | 実PG＋公開JDBC probeでautoCommit、prepare/bind/query/read/close故障、NULL列/欠落/重複 | false、SQL NULLを0扱いしない、例外秘密を漏らさない |
| PT-DB-INBOX-046 / preservesTransactionAndBusinessState | caller transaction/SELECT前後の状態、rollback/close probe、後続独立SQL | 検査はSELECTのみ、commit/rollback/close/SAVEPOINT0、callerが所有継続 |
| PT-DB-INBOX-047 / concurrentInspectionsDoNotCross | 100件・8thread・同じinspector、別connection/fixture/owner | 全futureの明示boolean期待一致、状態混入/更新なし、失敗をskip扱いしない |
| PT-DB-INBOX-048 / boundaryDescriptorsAndFrozenSnapshots | N9/record count/path境界、後続DB変更、反復/非秘密diagnostic | 有効境界通過・矛盾保持、保存済query値の凍結維持、4種coverage100% |

## 3. 実行と証跡

421のJDK25/Maven/PG18、対象commit/branch/command/日時/exit/expected/actual/BUG/SSC/hashは014とevidence/non-authentication-inspection/manifest.jsonへ確定する。関連認証/DB/codec PTを併走し、正式root clean verify、全PT、NullAway/SpotBugs、line/method/class/branch100%でのみslice合格とする。failed/flaky/skipped/not-runは合格へ算入しない。IT/STと実NK CHRは未実施。
