# NK-WEB-002 Web実行時JDBC依存 PT実行結果

BUG-233修正前RED: source `0a8257bc`、Web POMの`org.postgresql:postgresql:42.7.13`はtest scope。Maven dependency plugin 3.9.0 `build-classpath -DincludeScope=runtime`にJDBC jar0件。新PT-SCR-132の初回実行もscope不一致で失敗した。これは障害再現であり合格に算入しない。

修正候補の選択試験: Web POMを`runtime`へ変更し、PT-SCR-132 1件PASS、Maven runtime-only classpathの同jarは1件。test/compile/system/欠落scope、version相違、重複宣言の負変異を独立拒否する。全reactor・静的解析・coverage・証跡の正式gateは未実施であり、本書の選択結果だけでBUG-233を完了にしない。credential、classpath全文は保存しない。
