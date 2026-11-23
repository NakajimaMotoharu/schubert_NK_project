# Schema履歴末尾と物理行の単体試験仕様

NK-OPS-001、`SchemaHistoryAdmission.inspect/verify` と `Row`。WBS-P019-01.02/2の局所判定とF03へ接続。SS331・SS343のSSC396、SSC461、SS354、451。対象製品Core `87927ea17c1c8dbef528bc0c6882c24b1fe7c871`、試験source `36eea327b62ba303d48fadfb4b946e33ed1ae2fc`、JDK25.0.4。

| Test ID | 合成入力と操作 | 独立期待値 |
| --- | --- | --- |
| PT-OPS-SCHEMA001～010、012～013 | 固定SQL、履歴行の欠損・余剰、同一故障instance、所有ResultSet/Statement、borrowed Connection、割込の時点、8並行owner | SQLは固定文とtimeout5。子資源各1、借用接続0。行・所有・例外優先順は既存fixtureの固定表。未知、null、連結、割込前後とclose中を分ける。 |
| PT-OPS-SCHEMA011 | rank1・version001・SQL・固定filename・checksum19・success trueのRow | success true、固定表示文、JDK25の六component固定順から独立に算出したhashCode 583197644。 |
| PT-OPS-SCHEMA014 | 移行末尾V029/V030の合成履歴と、短い旧履歴・V031・異なるscript・反転checksum | 一致だけ所定順で三行返却。各不一致はSQLState 08001。全系列で子資源各1回close、借用接続close0回。checksumは合成固定29/-30、実Flyway値とは別。 |

実行 `python3 -B evidence/01_PT/018_NK-OPS-001/input/5792_p0190102_schema_history_same_exec.py`。一つのexecで14成功、失敗・error・skip0。二物理の無filter L93/M18/C2/B72、欠落0。BUG-3680/3681とYKT-2893の試験整形・例外宣言結果はPG43176に保存済み。実DBでのV030適用、移行や権限を含む全体451は保留。

[実行結果・環境・hash](evidence/PG43178-p0190102-schema-history-single-exec-v1/manifest.json)
