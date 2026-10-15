# YKT1065 全Main例外edge・実回帰照合

PG3416 actual0、candidate4856、公開 `PG3416-failure-graph-scope/manifest.json` SHA256 **be41c0565cc16f284e9ab6bf16e6a6125611c671770e2154d6ffa55f91a5afec**。関連902/903、SS314/324/331/352/451。全MainをgetCause/getLinkedException/getNextException/getSuppressedで検索し、32file/48access、未分類0。全対象path/行/code/hash/個別理由はmanifestへ列挙し、candidate Git blobと全対象source byteを照合した。

| graph handler | 修正/非該当根拠 | 実試験 |
|---|---|---|
| API OutboxJmsSender | 今回identity訪問済み/cause+linkedへ是正、suppressed二次duplicate非昇格 | 新cause3404三method、同八before/after |
| WebLogMessageSender | 既identity set/cause+linked、typed型だけ、cycle保護 | duplicateDetectionUsesTypedCauseAndLinkedGraphNotTextAndTerminatesCycles |
| RevocationRetryCoordinator | 既identity set/cause+suppressed、fatal objectを同一で再throw | rerun005gFatalIdentityNestedCyclicFailuresAndResourceAfterconditions |
| SessionStoreException | 既identity set/cause+suppressed、transient graphをcatalogへ保持しない | 新SessionFailureGraphTest |
| AuthenticationInfrastructureException | 既identity map/suppressed graph、JDBC二次fatal保存という固有契約 | 新AuthenticationFailureGraphTest |

五handlerは元PG3408/3409の実XMLから正確なclass/method一件・FES/flaky0・hashを回収し、候補の同componentへ接続。検索だけの完了0/追加試験再演0。その他のMainは一段unwrap四箇所（Future/JMS awaitまたはcloseGroupsの固定wrapper）、あるいはsuppressed配列長だけの有限判定。例外nodeの再帰/追跡loopがなく同causeで非終了しない理由とsource hashを各対象へ保存。異なるfatal/duplicate契約を混同せず、Web→API依存や新一般共通化0。

これは横展開の局所実証であり、当candidate全3712/新native/終端依存前にBUG1299/YKT1065全閉鎖とはしない。未網羅と正式受入・F03・QA051finalは別未完。管理照合の新Production PT加点0。
