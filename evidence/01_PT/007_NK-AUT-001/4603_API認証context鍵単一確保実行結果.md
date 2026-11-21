# API認証context鍵単一確保 実行結果

NK-AUT-001、WBS-P018-10.03、PT-AUTHCTX-KEYOWNER-001、BUG-3486、YKT-2779。旧PG41370は二cloneとMap.copyOfを観測。PG41372の現候補は全設定検査後の一回確保と固定32 byte領域の二copy。公開constructorと既EnvelopeFactoryを保つ。

Root NullAwayおよびWerror付き通常11件が全成功。PG41374で単一execのCRCと当classの行121・method 12・class 1・分岐38の全到達、Checkstyle・PMD・SpotBugs指摘0を確認。constructor命令89は全到達。既close命令6の未達を残す。実鍵・認証context・DB・実環境は操作なし。全451は保留中。

YKT-2779の現候補ではWeb log、失効、Web session、認証contextの四つを局所確認した。FingerprintKeyRingとResponseSnapshotCodecのclassfile・compile・通常PTはQA056で保留している。

[元構築](evidence/PG41370-p01810-auth-context-ownership-baseline-v1/manifest.json) · [通常11](evidence/PG41372-p01810-auth-context-ownership-qualified-v1/manifest.json) · [独立結果](evidence/PG41374-p01810-auth-context-ownership-independent-v1/manifest.json)
