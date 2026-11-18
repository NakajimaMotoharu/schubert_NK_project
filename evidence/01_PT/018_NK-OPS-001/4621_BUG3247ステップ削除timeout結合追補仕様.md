# STEPTX461007 所有者付きtimeoutの読み戻し

[根拠と初回6件](4620_SSC461ステップ削除JDBC伝播単体仕様.md)。BUG-3247。既Log用の本物のGuard interfaceのpositive pathを借用し、外部の認証・bind・ロックを使用しない。SS341 §7.3のtimeout秒floorと固定SET、後続DB変更前の値照合に対応する。

2.9秒の固定残値で整数timeout 2秒、SET bindの文字列2000と戻り2sを独立に定義。DB接続の代わりにこのケースが所有するメモリproxyにSQL literalを渡す。2sで正常commit／restore、行と文を4対解放。別fixtureで3sを返すと後続参照・変更0でbegin／rollback／restoreだけ、固定DATABASE_FAILURE、行文各1解放・借用接続close0を期待する。実DB・権限・Guard親class/runtime・実環境未起動。旧全6のassertと保全結果を開示し、新sourceでは全7を一回独立検証する。
