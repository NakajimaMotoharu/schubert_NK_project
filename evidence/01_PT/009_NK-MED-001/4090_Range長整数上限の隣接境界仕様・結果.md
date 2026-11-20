# Range 長整数上限の隣接境界

PT-MED-RANGE-LONG-001、WBS-P009-04/2、SS333 §10.1–10.2。仮定総長はLong.MAX_VALUE、上限1,048,576。開始9,223,372,036,853,727,232に上限差1,048,575を足すとLong.MAX_VALUE。末尾は総長−1の9,223,372,036,854,775,806、長さ1,048,575を期待する。開始位置を1だけ増やすと規定演算がLong.MAX_VALUEを超えるため、範囲なしを期待する。独立根拠は固定10進数とPythonの整数計算。既通常・無効・null・並行の5件を保持する。

2026-11-21、JDK25.0.4。選択1件・境界2件成功。失敗・エラー・スキップ・未実行各0。書式・Checkstyle・警告エラー化コンパイル終了0。独立計測で当runのCRC一致。旧物理は同sourceから `-g` を付与したコンパイルで5/5一致し、当runの元CRCとは分けて記録した。元PTは再実行なし。実HTTP、配信資源の後条件、全451を継続する。

[当試験](../018_NK-OPS-001/evidence/PG41190-range-long-cap-neighbors-v1/manifest.json) [独立CRC](../018_NK-OPS-001/evidence/PG41192-range-long-cap-independent-v1/manifest.json)
