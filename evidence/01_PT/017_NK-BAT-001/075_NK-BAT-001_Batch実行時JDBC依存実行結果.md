# NK-BAT-001 Batch実行時JDBC依存 PT実行結果

BUG-234修正前RED: source`1822055b`のBatch POMではPostgreSQL JDBC42.7.13がtest scope、Maven dependency plugin3.9.0 `build-classpath -DincludeScope=runtime`のjar0件。PT-BAT-283初回はscope不一致で1 failure、未実装のTDD初回失敗を合格に算入しない。

修正候補の選択結果: Batch POMのdriverをruntimeへ変更し、PT-BAT-283 1件PASS、Maven runtime-only classpathでjar1件。正式`PT-WEB-20260924-31`/source`fecc1181`はPT-BAT-017の旧依存allowlistで381件中1 failure/exit1（BUG-235）、不認定。旧PT-BAT-017の独立expectedに外部JDBC driverだけを追加し、選択PT-BAT-017/283 2件PASS。API/Web/Protocol禁止は維持。新正式全reactor/coverage/静的・48scope/hashは未実施のため、BUG-234/235を完了にしない。
