# NK-OPS-001 Expiry観測・削除境界 PT実行結果

PG247/SSC-078/BUG-238/YKT-189。PT-OPS-MQ-023/024/026/027の選択試験は2026-09-24 14:44 JSTに`ArtemisExpiryPurgeClientTest` 5/5、failure/error/skipped0。`observe`の削除呼出0、固定run/観測値の検査、削除前のcount/byte/selected drift拒否、実brokerの同時刻保持・+1ms削除を確認した。Batch `clean verify`は14:51 JSTに全396PT、failure/error/skipped0、JaCoCo全check達成、Production SpotBugs0。対象classのinstruction306/306・branch42/42・line59/59・method7/7・class1/1。`019_test_evidence_set.py`負canary99/99。source固定commit・全reactor/全scope/hash前のため**PG247は正式認定へ算入しない**。

正式結果の日時・OS/JDK/tool、branch/commit、command/exit、Test ID別入力・独立期待/実際、coverage/静的、関連BUG/SSC、証跡path/hashは後続の同一source正式runで追記する。V022のDB stage commitと実broker removeの接続、same-run再実行、失敗時/不確定commit、critical/health起動判断は未実施で、SSC-078/BUG-238/YKT-189も対応中。
