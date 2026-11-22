# Storage所有試験の例外型

NK-OPS-001、WBS-P003-08とF03/2-2-b、RD OPS009/FIL001～009、UI237/251、SS333/354。1969の `PT-OPS-RSCOPE001～008` と `PT-IOFACT-001～018` を使用。原仕様は元の入力・期待値、例外優先順位、資源の開閉順、有限待機に適用する。[既単体試験仕様1969](1969_StoragePureResourceScope_単体テスト仕様書.md)

BUG-3613／YKT-2843。候補の正規Storageから許可済みの実使用7物理を固定し、`ResourceScopeTest` と `FactoryResourceScopeTest` を厳格Java 25コンパイル。八メソッドの包括宣言を `StorageIoException`、`IOException`、有限待機の例外へ具体化した。四importと八宣言を逆変換すると、入力と期待値を含む全bodyが元ファイルに一致した。

対象 `1bba60f21849362b92b8a128464312a78134a647`、PG42774、通常26成功／2 suite。新定義0。旧包括SpotBugs8→0。例外を投入して同一性を確認する `raise` の2指摘、有限taskのPMD15とfinally内で停止・待機するexecutorのPMD3は原報告と適用理由を維持した。Checkstyle0。静的抑制・手動除外0。取引や実resource、Storage保留2、正式451の実行なし。[PG42774](evidence/PG42774-f03-storage-resource-fixtures-checked-scope-v1/manifest.json)
