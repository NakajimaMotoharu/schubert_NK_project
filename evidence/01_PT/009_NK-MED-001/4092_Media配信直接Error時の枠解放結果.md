# Media配信の直接Error時の枠解放結果

2026-11-21、PT-MED-PORT009、JDK25.0.4、選択1件成功。失敗、エラー、スキップ、未実行各0。元Errorが同一で、初回response／取得／closeは各0。次回は同instanceで206・3 byte・close 1。旧8メソッドを再演せず、新メソッドとJavadocだけの差であることを逆変換で確認。書式、Checkstyle、警告エラー化compile終了0。原XML・exec・当classのCRC一致を確認した。実HTTP・原本・配信・全451は所定の終了条件が残る。

[PG41194の内容、終了と証跡hash](../018_NK-OPS-001/evidence/PG41194-media-range-error-releases-permit-v1/manifest.json)
