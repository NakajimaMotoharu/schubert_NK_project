# Batchメモリmetricの並行一次診断

WBS-F03/2-2-b、SS351/354、BUG-3951／YKT-2997。元の独立文字列、二所有、64件と最大時刻、2/4/8 worker・10秒を保持。メモリ内のregistryと出力probeだけを使う。JVM/GCの収集や実scrapeの試験は選択しない。期待値の出典は次の元仕様。

| ID | 選択メソッド | 試験仕様 |
| --- | --- | --- |
| BATCHTEXT024 | BatchMetricTextTest#batchtext024FiniteConcurrentCallsKeepBorrowedOwner | [1777](1777_BatchMetricText_単体テスト仕様.md) |
| BATCHFULL011 | BatchMetricTextTest#batchfull011ConcurrentBorrowedSourcesNeverMixOrClose | [1833](1833_BatchFullText_単体テスト仕様.md) |
| BATCHREC007 | BatchMetricRecorderTest#batchRec007SixtyFourParallelSuccessesKeepExactCountAndMaximumTime | [1611](1611_Batch二Metric記録_単体テスト仕様書.md) |

共通の一次例外と抑制例外の挙動は既存のBatch fixture診断を参照する。実行終端を現正規Batch JARの単一runに記録し、生coverageを対象クラスだけ出力する。
