# Webセッションcodecの鍵確保 実行結果

NK-WEB-001、WBS-P018-10.03、PT-WEB-SESSIONKEY-001、BUG-3485／YKT-2779。PG41364は旧二clone、PG41366は全検証後一回確保と固定32 byte範囲copyを確認。実データ操作0。Gson 2.14.0、Protocol既正規JAR、JDK 25.0.4。

Root NullAway／Werror付きの通常9件全成功。元単一execとCRCをPG41368で照合した。対象classの行108・method 10・class 1・分岐42が100%。constructorは命令86まで全到達。既closeの命令6未到達を保存。Checkstyle、SpotBugs、PMDの対象production指摘0。実session、DB、実鍵、実レイヤ統合と451は継続。

[元構築](evidence/PG41364-p01810-session-ownership-baseline-v1/manifest.json) · [通常9](evidence/PG41366-p01810-session-ownership-qualified-v1/manifest.json) · [独立結果](evidence/PG41368-p01810-session-ownership-independent-v1/manifest.json)
