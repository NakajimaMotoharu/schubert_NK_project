# Logout再送行の純値境界 単体仕様

NK-WEB-002、WBS-P015-05/2、QA-050、SS314 §10、SS331・351・354。対象は `ClaimedRevocation` の値構築と保持情報。

| Test ID | 独立した入力と期待値 |
| --- | --- |
| PT-OPS-RVR-CLAIM001 | 固定requested時刻からlease終了＋1μs、既知expiry＋10μs。0及び100試行を受理し、任意expiry／payloadの欠落を保持する。固定の7項目、同じ記録の等値と固定伏字表示を確認する。 |
| PT-OPS-RVR-CLAIM002 | −1／101試行、requestedと等しいか前のlease／expiry、DBに保持できない1nsを拒否する。発行者と実DBの所有権はこの値から導出しない。 |
| PT-OPS-RVR-CLAIM003 | identity、key version、lease owner、lease時刻の欠落、およびversionの形式違いとpayloadとの不一致を拒否する。 |

試験には独立した固定時刻、合成UUID、固定長のゼロ埋め配列を使う。実DB・JMS・root・暗号処理／鍵は不要。JDK25.0.4、JUnit Jupiterと単一execの生JaCoCo。旧SQL代理試験とrawを合算しない。実lease CAS、JMS待機中の接続解放、停止順序は別検証。
