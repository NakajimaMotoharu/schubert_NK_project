# BUG-3262 API JVM・System metricの通常単体仕様

NK-OPS-001、RD171/UI252/SS351/354、WBS-F03/2-2・P018-09、YKT-2387/2691。元[2841](2841_API標準SDK三whole44_単体テスト仕様.md)のAPIJVM001〜014、APISYS001〜014と製品Mainを保持。該当二箇所のowned executor終了、固定modeの完全一致拒否を追加する。

- APIJVM014／APISYS014は、それぞれ4 worker、64独立owner、4/2処理と計256/128、借用source・Future.get 10秒を維持。finallyで停止し10秒以内に全worker終了を確認する。
- APIJVM005／APISYS005へ、前回[4647](4647_BUG3261APIGC固定mode不正値仕様.md)の同hash異値二つを入力へ追加。期待は固定CONFIG_INVALID、registryへ未到達、factory未取得。許可値と不正値の区別は元固定文字列と独立Java hash計算を参照。

自己所有JVM内のSDKとfixtureだけを使用。運用registry、HTTP、外部JVM、DB、nativeを扱わない。通常28、Root静的、独立XML/CRCと対象生counter。保留や補助型の未到達を別記する。
