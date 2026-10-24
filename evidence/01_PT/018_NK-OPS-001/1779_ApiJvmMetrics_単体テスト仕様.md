# API standard non-resource JVM binder PG/PT仕様

NK-OPS-001/RD171/UI252/SS311351/411/451、PG-D605/group2006、WBS-P018-09/C07参照0加算。fresh31残69/reset1793382075/1-3-6pp/cap10はPG8472/event2006固定。SS351 §6はJVM/GC/thread等を標準Micrometer metricへ指定、既srcに四SDK binder/ApiJvmMetrics導入なし・後続索引一致0。既core1.17.1 SHA9ca47dfa831409b40253c8dc98c17b9d3e050ebbde4d1543c5521dca2b95ad56の公開javapでClassLoaderMetrics/JvmMemoryMetrics/JvmThreadMetrics/UptimeMetricsはMeterBinderのみ、JvmGcMetricsはAutoCloseable/close/listenerを持つため別の必要依存と確定。

## 製造
ApiJvmMetricsはAPI固定service=API tagで上記四標準binderを借用registryへ登録する。STANDARDはfactory/JMX/source未読、DEBUGはsource閉鎖確認→factory一回→deep immutable binder list/全4要素nonnullを確立して順にbind。factory/binderの元Runtime/Errorを伝播し、partial registryの所有はcallerに残す（暗黙rollback/source close/再試行しない）。自身はsource/handle/registryを保持せずGC listener/CPU/FD/標準text/endpoint/actualroleを完了化しない。POM/Bootstrap/Web/Batch/旧全MainとUnit/上位不変更。

## 新APIJVM001～014（14/1）
1. 実own JVMのDEBUG四標準binder、literal namespace/固定API tag、class-memory-thread/time系を確認。固定process start timestampは独立RuntimeMXBean値、uptimeは独立前後時刻の範囲。動的class/thread/memory値は外部SDKの非負/存在契約を確認し、性能値/IT-STの合格にしない。
2. STD factory0/source closed/getMeters読取0、DEBUGのSDK/JMX初期化を遅延。
3. 四portの固定順1-2-3-4/同borrowed source/factory一回。
4. null source/mode/factory拒否。
5. unknown mode（空/小文字/末尾空白/未知）拒否、factory0。
6. closed DEBUGはfactory0で失敗、再openしない。
7. factory返却null/list要素nullを全bind前に拒否。
8. binder count0/1/3/5を全bind前に拒否。
9. factory Runtime/Error同identity。
10. 各位置binder Runtimeで後続未実行・primary同identity・partial sourceはcaller所有。
11. 各位置binder Error同様、成功化しない。
12. closed source STD未読/全4port未実行、暗黙closeしない。
13. 二owner/同instanceの再利用でsource保持/状態漏れなし。
14. 有限64並行・独立4port/owner/回収join10sec、sleep0。

動的値のexpectedをproduction factoryや同SDK binderから生成せず、固定literal・独立Java公開management API/port記録を用いる。対象はfresh own host JVM内だけ、他process/実VM/Root/DB/鍵/Backup/permission/ネットワーク/サービス/拒否再試行0。SDK依存byteは既normal/descriptor/pinの同一品、入手/更新なし。

新normal六/NullAway/format→original14（一exec）→新Main1実line-method-class-branch100/PMD-CS-SB-missing0/CRC0/session1→全physical/owner/role/新class fields0→1780。command/環境/OS-JDK/branch/source/時刻/exit/input/expected/actual/XML/exec/counter/static/log/hash/BUG-YKTを新only公開manifestへ。既成功の確認再演/別source coverage合算なし、実装済み違反は修正前915/916へ。現在PT/coverage UNRUN。

正式1964-53/原190新受入0/工数null/QA051final/PTALT0/whole451/CHR/F03Root11/actual VM-Root-DB-native-Backup-鍵-intent-permit-配備/拒否未特定HOLD、元-v4-v5/欠測不変更。GC/CPU/FD/標準text/actualendpointは別未完、通常区切り停止なし。

