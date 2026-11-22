# SSC-477 同期Handler型と受信情報の実行結果

PG42724、`dev-foundation`、対象 `02ef1afa67e4d6950063aa034421dec478064f8a`。確定設計はmainのPR444、`ca41c03c0c6efff9a3a35b47b480491810bee6f9`。[単体仕様](046_SSC477同期Handler型と受信情報の単体仕様書.md)

| 項目 | 結果 |
|---|---|
| PT-JMS-HCTX001～005 | 5成功、failure／error／skip／未実行0 |
| Java25とNullAway | 対象と直接依存の限定compile終了0。Jdk25.0.4、NullAway0.14.1 |
| 静的 | PMDとCheckstyleは0。SpotBugsは製品指摘0、試験の意図した5つのnull投入を生報告で保持 |
| RequestContextの単一exec | 生L13／M10／C1／B4、全数到達。命令85、未到達0 |
| LayoutHandler | 三抽象methodのみ。実行可能命令なしを物理収録表で確認 |

PG42722の初回5成功と適用PMD1件を履歴に保全。BUG3608/YKT2838を修正して現sourceで再試験した。入力と出力のhash、個別Test ID、実OS・toolchain、固定commandはmanifestに接続する。registryの製造、実dispatcherの31呼出、認証後のactor・受信時刻の引渡し、JMS・Inbox・全451は次の受入条件。正式受入加算0。[PG42724](evidence/PG42724-ssc477-request-context-and-handler-v1/manifest.json)
