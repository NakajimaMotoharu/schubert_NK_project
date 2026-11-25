# QA049並行fixtureで一次失敗を保持する単体仕様

NK-WEB-001、WBS-P015-01/2、QA049、SS314 §7.2.1／SS354、BUG-3908／YKT-2997。既存TOKV205の合成JSON・固定v2属性・10/11件容量・100独立作業の手書き期待値を保持する。10worker、Future20秒、停止確認10秒を既Web共通workerへ接続し、処理本体と終了解放の両方が異常なら元の診断を保持する。workerの二異常の独立期待値は既ViewFixtureWorkersTestの実績に照合する。

現SessionAttributeCodec、SessionAttributes、SessionOperationTokenと必要な値・例外だけを固定し、ProtocolとGsonの固定依存を使う。現鍵、HMAC、暗号化、セッション保存、DB、認証、実tokenを扱わない。終了値・XML・生指標・静的結果・sourceとhashは5845とmanifestに記録。元12の結果を合算しない。
