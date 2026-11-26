# Batchの合成観測と並行試験の一次診断

WBS-F03/2-2-b、SS351/354、BUG-3941／YKT-2997。元の固定値、8並行・64観測、10秒の一括実行と終了を保持する。二つのFileStore条件は手製の合成実装、ヒープはMemoryMXBeanのJDK代理を使用する。起動中のJVM管理サービスや実FileStoreを使わない。期待値の出典は次の元仕様。

| ID | 選択メソッド | 試験仕様 |
| --- | --- | --- |
| FSINPUT007 | FilesystemHealthObservationTest#fsInput007NullAndConcurrentIndependentReadsDoNotAcquireOwnership | [1582](1582_FilesystemHealth観測_単体テスト仕様書.md) |
| FSINPUT010 | FilesystemHealthObservationTest#fsInput010NullBackwardsGapAndConcurrentPollHaveOneSerializedOwner | [1582](1582_FilesystemHealth観測_単体テスト仕様書.md) |
| HEAPINPUT008 | JvmHeapHealthObservationTest#heapInput008ManyBindingsDoNotReadOrMutateAndConcurrentReadsAreExact | [1591](1591_JVMHeap健康入力_単体テスト仕様書.md) |

共通の一次例外と抑制例外の挙動は既存のBatch fixture診断を参照する。実行終端を現正規Batch JARの単一runに記録し、生coverageを対象クラスだけ出力する。
