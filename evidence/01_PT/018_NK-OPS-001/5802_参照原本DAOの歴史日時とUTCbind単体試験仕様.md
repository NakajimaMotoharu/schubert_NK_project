# 参照原本DAOの歴史日時とUTC bind単体試験仕様

| 項目 | 内容 |
|---|---|
| Program・対象 | NK-BAT-001 `RunReferenceRepository.read`、PT-BAT-UTCPORT001、WBS-P004-03/2。WBS-P004-05/2は証跡参照。 |
| 上位仕様 | DAT-009／OPS-009、UI251、SS331 §3.12、SS332 SSC056、SS343、SS354。 |
| 事前条件 | 当Coreの正規Batch・Bootstrap・Storageから既承認の九物理を照合する。既存の独立JDK proxyを使用。実DB、実ファイル、権限・保持操作は不要。 |
| 入力と操作 | 1582年10月4日と14日、1900年境界、1970年境界、現代マイクロ秒の明示offset五組をInstantとして渡す。別JVMの既定タイムゾーンはAmerica/New_Yorkとする。 |
| 期待値 | Java fixtureに記した独立UTC literalとbind位置2の型・値が一致。位置1は借用呼出元の固定UUID。取得した行と文を各一回閉じ、接続の所有を変えない。期待値に製品変換を使わない。 |
| 観点 | 正負offset、翌日・前年・epoch、6桁の小数、借用接続。null／SQL異常／並行はPG40270等の既存試験IDへ個別対応。この五組で実Driver投影やsession timezoneの実績を代替しない。 |
| 実行と証跡 | 追加した一methodを選択し、対象commit、JDK、引数、XML、個別counter、終了値と証跡hashをPG43224に記録する。 |
