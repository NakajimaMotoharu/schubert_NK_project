# Storage例外グラフ・理由カタログの現候補試験結果

PG43556、固定候補 `4ec7fc22ee08b2d884d1b9d5c542a12d58fbf6b1`、製品Core `87927ea17c1c8dbef528bc0c6882c24b1fe7c871`。PG43150の正規Storage JARとMain treeを再照合し、二物理を使用。PG41294のグラフ7件と、改訂済みのfixtureを含む理由カタログ1件を選択した。2026-11-23、JDK25・JaCoCo 0.8.15、終了0。成功8、失敗・エラー・skip・未実行0。既存8件の測定で、新定義0。

SS333／354・SSC439／461の局所値契約。理由名・順序・返却配列の別の有効な値への書換え・例外の公開メッセージとcauseなし、循環を含む非fatalの非破壊走査、cause／suppressed／追加辺の順序とfatal同一性を既存のリテラル・JDKメモリの独立期待値で確認した。

| 型 | 行 | method | class | branch |
|---|---:|---:|---:|---:|
| StorageIoException | 23/23 | 5/5 | 1/1 | 12/12 |
| StorageIoException.Reason | 4/4 | 5/5 | 1/1 | 0/0 |
| 計 | 27/27 | 10/10 | 2/2 | 12/12 |

PG41294とPG43354のexecは別々に保全。今回の二物理には一回の現候補測定を使用。実JDBC／native・保留二試験と六製品451は未受入。

- 公開manifest `evidence/01_PT/018_NK-OPS-001/evidence/PG43556-current-storage-values-eight-single-exec-v1/manifest.json`
- SHA-256 `030709273f27defec56de15ec81b2b0053d8ed22482589d78bf19bb4fe49f037`
