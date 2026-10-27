# 2186 Batch標準source owner例外保全結果

2026-10-27/dev-foundation、製品Test source862cce50220c6ce186c084504756a7fbb9978270/Main21d不変。2185 F03-BATCHGUARD001..004、BUG1908/YKT1659/PG-D702。14owner取得直後の外側try/finally・016executor TWR、原全16method/全oracle token・明示close/retry順/identity/各10秒期限/元finally release-shutdown-await-closeを保持した。追加owner cleanupはMain既冪等closeにより正常結果を変えず、015/011～013/016で元counts/order/所有を確認。

|公開証拠（provisional/<run>/manifest.json）|SHA256／真正結果|
|---|---|
|PG11318-batch-source-guard-plan-v1|9e5ded873f7abbb9ee67331a1ab109899375b627c084739cfdf2270a00cc34b6／14guard/一TWRだけ|
|PG11320-batch-source-guard-source-post-v1|e89b43adb750c274989111a51181f8b555601282057cec618aa4a0b942095c62／独立元全token逆・各guard/誤owner/Test無効/欠TWR/期限の31metadata反例0|
|PG11322-batch-source-guard-six-compile-v1|066e1c301187c43224e8ab120c50889ef8a832f48de3fe4406aa7e533ac14e27／正常六compile/package0・PT0|
|PG11324-batch-source-guard-host-v1|bf9b6663633c9091069a107d82af3d7dc83548a8c86340cf453c020cd8a5d6e6／元16一suite・F/E/S/aborted/containerfailure0・producer/JVM0|
|PG11326-batch-source-guard-static-v1|038ece1f7b1c1c0f04c651f829688a661788756d3c68cface349a5bda2104623／当raw23→8・Close17→2、CS-processing0・gate1保持|
|PG11328-batch-source-guard-post-v1|c5ce52f97e1ef5762f071d6006b0efdc9df2801b00efb98bbd77f0707f618806／元XML/一exec/完全Batch/session/CRC・六反例0|
|PG11329-batch-source-guard-context-v1|fd78b2d6728898510ce9e585e0613a0477f8fd67be8a6298ac315aad633be6f7／六thread具体文脈、二ProbeGc未分類raw保持|
|PG11331-batch-source-guard-context-post-v1|e8ec88ebb4a1fffad43de5f3b1ff47bcc46ad54bb437bd33092ccd2e4255bce6／十metadata反例0|
|PG11330-batch-source-guard-trace-v1|91a431e8ffc0240f64f729ca7e7e6ce6894b4bab35aee82ea9f64317ff9687b0／元一P01809 SHAだけ/他982row・全歴史保持|
|PG11332-batch-source-guard-trace-post-v1|d2388f5433da5cfc79685ef3b52fa550a1e2071cdf3de8db8b1cb8648183d2f9／六反例・原941943/予算/acceptance保持・全audit前後1同HOLD|

実入口は共通 `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/<各run対応entry>.py`。原manifestはOS/JDK25.0.4/Maven3.9.12/SDK・静的tool/command/env/branch/source/実時刻/exit/全input・jar/XML/exec/hashを結合。guard失敗辺はJava finallyと独立構造逆/変異拒否で確認し、意図的にJUnitを失敗させた実行を成功件数に加えていない。元d431/107成功と静的反例11312を保全し、当sourceへ合算0。

当Main BatchStandardMetricSourceはL40/M9/C1/B16 covered・miss0。単一session PG11324-BATCHMET-JP、完全Batch645=644解析＋真の空metadata一、covered-missed L115-18301 M32-3173 C6-407 B34-8424で全体未達。全Main1843 code/debug/byte不変、他Test1959不変／当一SourceFile由来3物理差。除外/oldexec union0、own空CWD前後不変、外部process/VM/Root/DB/鍵/強制GC/保留依存操作0。

残8はthread6の通常JUnit own2worker/latch・割込復元/元10秒期限・owner外側guard/executorTWRを元ID/現座標/hashへ対応しraw保持・全体pending。CloseResource二つはProbeGcのcomposite移転依存で未分類保持、guardを追加しただけで一括非該当/全raw0へ変換しない。BUG1908当14owner＋executor一はPG_PT_FIXED_VERIFIED、YKT1659当15是正範囲SCOPE_COMPLETE、完了2026-10-27、修正862cce502。原31分類の7直接closed/1GC finally/6Fake未分類も元2184に保持、全F03/451認定0。

開始1/4/8共有pp cap10・fresh最終使用32残68/reset1793599188、共有丸め差0≠専有費0、N/T/専有費/工数null・usagef832a059。正式1964PT/53scope・17/190・QA051final/全安全HOLD不変。次は元8973への当15既是正の元ID結合、残具体資源の所有・未分類/次独立PG/PTへ継続する。通常group/commit/レビュー/PMO待ちで停止しない。
