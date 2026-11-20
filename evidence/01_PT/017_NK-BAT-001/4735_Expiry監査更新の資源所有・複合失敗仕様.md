# Expiry監査更新の資源所有・複合失敗

NK-BAT-001／DAT-009／OPS-009、UI251、SS331・332・341、SSC310、WBS-F03/2-2、BUG-3408／YKT-2732。

**EXPPORT-J010**。stageとfinishの各fixtureで、借用Connectionの参照照合を通過し、取得済みPreparedStatementのUPDATEは合成LinkageError、closeは別のSQLExceptionを返す。期待値は一次Errorの同一性、抑制例外一つの同一性、文解放一回、Connectionを解放しないこと。所定のJava25 TWR順序から独立に定める。

PG40726の29件と追加J010を、当source・同一execで実行する。元のSQL・bind・取引所有、早期・null・標準例外の既期待値を照合し、局所物理の生4指標とinstructionを除外なしで測定する。実DB、保守処理、他プログラムの回帰、正式451は各開始・終端条件に従う。
