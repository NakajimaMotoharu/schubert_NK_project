# 1680 Async Queueバイト割合是正 結果・横展開

1679/PG-D552/BUG1665-YKT1416/group1897、修正source `8f6b3bff2845ce99276dfb56046a473f7715e4f6`。通常202PT/27suite（追加是正2＋必要既200）を同sourceで全実行。期待値を件数から独立したSS351/321のbyte割合へ訂正した。旧6247/200とd56/192は各sourceの歴史成功のまま保全し、本結果へ合算0。

| provisional原run | 結果 | manifest SHA256 |
|---|---|---|
| PG7532-async-byte-unit-host-v1 | 真正0/202普通PT27suite/FES・flaky0 | 5fbec402855f1e3288d9424203e33eff313e7aff00bd31d1f16540a455bd8344 |
| PG7534-async-byte-unit-post-v1 | 全55Java/実49＋metadata1/単一sessionCRC0/L811 M187 C49 B363全miss0/NullAway-SB-CS0/raw28 exit4保持 | 11cf6da4a00b9bb8316cec7274ef6263110437336ff1dc7aeeb2b219e976ba64 |
| PG7536-async-byte-unit-six-compile-v1 | 六正常Main/Test compile-package0、PT0/UNRUN | fee7fc0882334091724f6251656bab0328643690377a8f277cc8576554bc4bd3 |
| PG7538-async-byte-unit-six-post-v1 | 全1750Main/元1669debug込み不変・当Batch50/歴史API21-Web10 byte-only/三POM・SDK・当五rule0 | 8e59fbd578d0c5b3b89e2734d11d0ad41d92ee94a6fc1bef3b35be7ec91bb29d |
| PG7540-async-byte-unit-trace-v1 | 全94source/81追加physical・編集6/不変88/新0・当Batch49だけcurrent PT | 662fa8a43b797e2ceafa2c2d6f3fe8ab9c449e6013cee1c6c601fc8eaf28bd81 |
| PG7543-async-byte-unit-review-v2 | raw28全理由/27同位置＋1行移動context独立照合/未分類0、生成23型82methodを当ordinaryへ結合/六domain負改変 | 03d1e311e2c32f5270138b0851afe03edfcee913b30df21e685534c51c84baac |

日時/OS/tool版/branch/source/command/終了code/inputs/XML/output/CRC/coverage/static/hashは上記原manifestから一意参照。host初回commandはpyflakes PYTHONPATH不足import exit1/PT0・snapshot/job作成前で、正規環境唯一7532/session59761が真正0。post3494/compile69361/physical94540/review2164も終端0、再実行不要。source変更中job0、旧成功確認再演0。

## BUG1665/YKT1416対象別結論

| 対象 | 修正・非該当根拠と再発防止 |
|---|---|
| AlertThresholds.asyncQueue | queued/usedBytes/capacityBytesへ分離、分子はusedBytes、count5000/9000とは独立OR。THRESH003/013/014で非相関・exact70/90・MAX overflow・負/0・64callerを再試験 |
| MonitoringPolicyEngine.asyncQueue | 三独立値を無変換で転送。既12condition/72keysに加えASYNCBYTE001で低count/高byte・高count/低byte・無効時event不変を確認 |
| AsyncQueueMonitor.observe/ByteUsage/Evaluation | Optional countとOptional ByteUsage、片側既知異常検出/欠落正常復旧0、byte invariantをconstructorで確立。修正ASYNCQUEUE8＋ASYNCBYTE002、生成6＋5契約も独立oracle/当class byteで確認 |
| 全呼出/Test/oracle/仕様 | rg asyncQueue呼出は上記Main三/Test三だけ、全箇所三次元化/旧二long入口削除。1679とPG-D552で旧1674/PG-D520/550を訂正、旧証拠は上書き0。7540の六編集hash/旧anchorへ結合 |
| FS/JVM HealthUsageRatio | used/maximumの同byte単位比で非該当、fromUsedの不正/上限超過UNKNOWNと既当回帰を保持。件数を分子へ混在させない |
| API DbPoolMetricRecorder.Counts | active/maximumとも接続数、今回のQueue byte比ではなく非該当。供給値の別family/跨時点同時性は認定せず、API歴史byte-onlyを当PTへ流用0 |
| Transfer/Expiry/WebLog | Transferはbytes/files別threshold・別gauge、Expiryは件数1000/5000、WebLogは件数とDuration。件数をbyte上限で割る処理なし、既当202回帰の個別独立vectorを保持 |

検索だけで閉鎖せず、全修正対象を202実回帰/当49実class四100と個別criteria・sourceへ結合した。BUG1665/YKT1416はこの純粋実装・oracle対象に限定してCLOSED、実queueの合成source/同時観測/owner/collector/通知/制御を受入した意味ではない。

## 品質工具の手戻り

原7542は既raw全位置一致の仮定でexit1、工具/failed manifestを707361c26へ保全しBUG1666/YKT1417起票。新7543は27同位置・同owner byte＋一件AlertThresholds.percentageの全method body不変/100境界の独立14PT/明示115→117行・他全属性一致へ分類。抑制/一括行無視/UNKNOWN成功化0。全28とMain三/Test三・raw0の変更箇所を点検し、六source/domain変異を拒否、元失敗/通常202成功を維持。BUG1666/YKT1417当review scopeを限定CLOSED、工具修正だけで普通PT/compile再演0。

当群開始3/5/9pp上限10・元-v4-v5/元窓0/reset1793306748不変更。元製造新規0、実装/oracle手戻り一・追加是正case2・既200当再資格、tool手戻り一を区分。専有費/N/T/工数null、正式1964/53/原190新受入0/QA051final/PTALT0/whole451-native-CHR/全actualHOLD不変更。実Broker/DB/Root/VM/keys/配備/拒否未特定操作0。
