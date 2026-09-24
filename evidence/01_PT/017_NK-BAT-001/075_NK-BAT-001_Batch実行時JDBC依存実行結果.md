# NK-BAT-001 Batch実行時JDBC依存 PT実行結果

BUG-234修正前RED: source`1822055b`のBatch POMではPostgreSQL JDBC42.7.13がtest scope、Maven dependency plugin3.9.0 `build-classpath -DincludeScope=runtime`のjar0件。PT-BAT-283初回はscope不一致で1 failure、未実装のTDD初回失敗を合格に算入しない。修正後の正式全reactor・証跡は未実施。
