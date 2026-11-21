# API認証context鍵単一確保 単体仕様

NK-AUT-001、WBS-P018-10.03、SS314／352、SSC421／422、BUG-3486／YKT-2779。PT-AUTHCTX-KEYOWNER-001の独立期待は事前検証後の1回確保と二固定copy、単一領域のclose。旧二cloneとMap.copyOfの順をbytecodeで観測。既暗号・AAD・EnvelopeFactoryと鍵versionの公開結果は維持する。

元PT-AUT-005、OWN001、FACT001～003の全11合成試験を一回の隔離JVMで再認証する。案件の実鍵・実認証context・運用processやDBを使わない。null、前鍵、失敗、nonce、例外、並行、closeを既独立ベクターで照合。Root NullAway、Werror、Checkstyle、SpotBugs、PMDと当classの生四指標を記録する。
