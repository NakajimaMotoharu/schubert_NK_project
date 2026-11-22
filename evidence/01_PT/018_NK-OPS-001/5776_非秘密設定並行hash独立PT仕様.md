# 非秘密設定の並行hashを固定fixtureから照合

NK-OPS-001、SS352、WBS-P018-01/2、BUG-3669／YKT-2885。PT-OPS-APICFG005／WEBCFG005。各fixtureの承認済みGOLDENのUTF-8 byteをJDK SHA-256で変換した一値を期待とする。元001／006（基本値・公開雛形）とAPI007の独立算出も同一fixture内で再利用。32個ずつの並行hashを比較し、異常null、未知key、5秒の各待機と10秒の所有終了を保持。

当候補BootstrapのApiNonSecretConfig、WebNonSecretConfig、JdbcFailureGraphと補助Storage二classを入出力に固定し、固定の公開三雛形のみ専用領域へ複製する。原14件を一回選択し、同一source/runで終了・当該二Mainの生counter・静的結果を記録する。実設定・秘密・認証・DB・JMSは参照しない。
