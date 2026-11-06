# 群末quota鮮度結合（品質工具・非Production PT）

対象 tools/quality/pmo_quota_binding.py:end_fields、BUG2322/YKT2067、477/487。既start_fieldsは変更せず使う。製品Java/DB/VM/API要求や実reset/券/課金を操作しない。工具のPython型・時刻・割合計算だけを固定入力で検証する。Main D8/正式1964PT/53scopeとは別domain。

|ID|独立期待値|
|---|---|
|QLT-QUOTA-END-001|前27→後28は共有1、専有費/実token null、attribution UNKNOWN|
|QLT-QUOTA-END-002|実終端より前の観測を拒否（BUG2322再現）|
|QLT-QUOTA-END-003|121秒経過・未来観測・receipt改変を拒否|
|QLT-QUOTA-END-004|使用90/95/100でも既結果の保全を記録し新実装禁止、89だけquota上許可|
|QLT-QUOTA-END-005|取得不能/拒否を保全、欠測を0としない・新実装禁止|
|QLT-QUOTA-END-006|reset marker差は同窓不成立・差分null、券操作/推定なし|
|QLT-QUOTA-END-007|同窓減少を拒否、27→35は実共有8/cap6超過を記録、capのNone/bool/0/11/NaNは拒否|
|QLT-QUOTA-END-008|該当secondary残10でも新実装禁止、primary共有1と混合加算しない|

公開driver `input/058_quota_end_guard_test.py` の8unittest methodに上表を順番で対応付ける。fixtureは固定UTC時刻・固定割合/markerであり実API観測の代用品としてeventへ登録しない。期待値は固定1/8/null/境界時刻でProductionコードから生成しない。テストはAPI・イベントwriterを呼ばず保全用の新しい自己所有slotにだけ結果を書く。

実command: `env PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/058_quota_end_guard_test.py pg20218-quota-end-guard-v1`。再現時は引数を新しい未使用 `pg<番号>-quota-end-guard-v<版>` にし原slotを上書きしない。環境は本host Python3、OS/tool/source hash・actual exit・8case結果はPG20218 manifestとunittest.safe.txtを参照。実quotaは別途get_usage_limitsの新観測をcaptureし、今後start_fields/end_fieldsで鮮度・終端・replayを結合する。工具8件をProduction PT/coverageへ足さない。

最新の回帰強化PG20222: 正規化receiptを工具で生成せず独立literal fixtureへ変更し、secondaryのfuture resetを固定して89/90の境界だけを分離。120秒ちょうどの許可とremaining改変拒否も追加確認。同じ8methodの最新実行0/FES0、元PG20216/20218は別sourceの歴史証拠で合算なし。target SHA f85c96354f54790923ee2bf930d099592a257d84844c13c641ff78ec9af0a3e6、driver SHA d166a81215e79953fc257014db4d0779ee8c1be089d298094f841a0f72a11fdd、最新manifest SHA 02cba035781ca0dfc8f4ad30564f713061cd53212e9543abb1a2af3a6436d8f6。旧20218 driver byteはPG20218-quota-guard-producer-history-v1で保全。
