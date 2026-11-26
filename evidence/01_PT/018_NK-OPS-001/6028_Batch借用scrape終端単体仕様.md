# 合成scrapeを借用中の終了順と一次障害

WBS-F03/2-2-b、SS351/354、BUG-3954／YKT-2997。対象は[BATCHHOST016](1810_WebBatchStandardMetricSource_単体テスト仕様.md)。注入ProbeRegistryとnoop binderのみ。先行scrapeが閉鎖を阻止し、latch解放後に固定文字列の返却・所有close・後続拒否を確認。2workerと全10秒待機を保持。予備closeは試験所有者の一経路とし、workerの終了より後に実行する。明示的な二重closeの契約は既BATCHHOST015に残し、今回再演しない。実scrape、監視、GCの採取は別。
