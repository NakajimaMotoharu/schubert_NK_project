# F02ファイルログhandlerの実行結果

NK-OPS-001、WBS-F02-a、SS311 §3／§5.2・SSC028、PT-F02-LOGFILE001～008、BUG-3478／YKT-2774。工具修正commitは `1c5e4f1675`。製品Core `a8913bc836f81632613b34243f84b7b15eb3e054` に変更なし。

- 修正前PG41286で禁止4件を検出できなかった。JDK逆アセンブルの回収時、6宣言には直接`openFiles`の5件と、その一つに委譲する1件があることを確認した。保存済みの元stdoutから再判定し、元の静的試験は再起動しなかった。 [修正前](evidence/PG41286-f02-jdk-file-handler-red-v1/manifest.json)
- 修正後PG41288は新8件と必要な既35件の判定が全一致。期待する違反23件を検査が報告し、期待非該当20件の誤検知0。ファイルを開くfixtureの起動は0。 [修正後](evidence/PG41288-f02-jdk-file-handler-fixed-v1/manifest.json)
- PG41290で現候補と同一入力の正規Protocol JAR 176物理、合成anchor五件、6,203依存、3,953呼出を解析。五規則各0。Protocol source169と既許可のController source13にFileHandler参照0。今回の実JARは1/6。 [独立物理](evidence/PG41290-f02-current-protocol-file-handler-v1/manifest.json)

コマンド、JDK、入力と出力SHA、終了コードは各manifestに記録。F02の六製品包装、API／Web、Storage旧JDBC辺、実runtime、451は未受入。製品PT、正式受入の加算0。
