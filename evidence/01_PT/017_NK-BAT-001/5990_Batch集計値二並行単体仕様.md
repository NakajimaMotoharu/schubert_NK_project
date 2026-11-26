# Batch集計値と試行値の並行試験の一次診断

WBS-P017-07.03/2、F03、SS331/332/341/354、BUG-3947／YKT-2997。元の64並行の値、5秒の個別結果、10秒の終了待機を保持する。各試験の独立した件数と時刻、元の例外契約を使用する。実DB、削除、原本保持、運用起動は別。期待値の出典は次の元仕様。

| ID | 選択メソッド | 試験仕様 |
| --- | --- | --- |
| PT-BAT-161 | CleanupStepValuesTest#concurrentValues | [026](026_NK-BAT-001_cleanup_step値_単体テスト仕様書.md) |
| PT-BAT-137 | BatchStepValuesTest#independentConcurrentValues | [021](021_NK-BAT-001_step値_単体テスト仕様書.md) |

共通の一次例外と抑制例外の挙動は既存のBatch fixture診断を参照する。実行終端を現正規Batch JARの単一runに記録し、生coverageを対象クラスだけ出力する。
