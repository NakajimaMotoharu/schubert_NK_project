# API標準SDK text所有source PG/PT

初回PT/source固定前の内部invariant補足:close開始でbound=falseとし、GC/registry closeが例外で未確認でも新しいDEBUG scrapeを拒否する。APIHOST012/013に拒否assertを含め、同16IDのまま保持する。新機能の未完成部分をsource固定前に補完したもので、実行済みPASS/期待を変更・転用しない。close未確認をclosedへ偽装せずcaller明示回収を維持。

開始後の準備追記（BUG1711/YKT1462）:8668はtracer親POM欠落でbuild/PT前に停止、元tool/同byte部分配置12を保持し再発行0。8669新準備で公開固定親POMとchecksumだけ補完し全20座標の全source/親を先行検証後に配置。SDK本体download0/既座標上書き0、公開親取得数と再現手順は8669へ。以下開始時「取得0」はSDK本体について維持、公開親補完は追加依存費として分離。

NK-OPS-001/RD171 MON010～013/UI252/SS311・351/PG-D614、主P018-09/C07共有費0、group2037開始fresh40残60/reset1793382075/3-6-10pp/cap10。431/1799/既StandardMetricsとCustomPayloadを着手前照合、標準SDK text出力ownerは未実装。既4222/旧部品確認再演0、旧1737parser等を新規進捗にしない。

src/api/monitoring/ApiStandardMetricSource 新Main1。固定official PrometheusMeterRegistry1.17.1/client1.7.0へ標準JVM/CPU-FD/GC binderを登録し標準textを出力、private sourceを公開しない。callerが所有objectを先に保持し、STANDARD取得0、DEBUG単回bind・GC保持先行・部分失敗は未成功/再bind不可。明示closeはGC→registry、失敗未確認はowner保持、同期化によりscrape/closeの同時交錯を禁止する。actualendpoint/権限/起動/health等は変更しない。

新APIHOST001～016/ApiStandardMetricSourceTest（予定16/1）。fixtureはdefault own fresh JVMのSDKと、package内factory/registrationポートの記録用fresh SDK subclass。期待は個別の固定count/order/元例外identity/呼出0/closed事実/独立Runtime.availableProcessors値と標準sample名、production methodからexpectedを作らない。

1. STANDARD bind/scrapeでfactory/registrar未読・空text、close前後も詳細取得0。
2. default DEBUG bind→official CPU count sampleの独立JVM値/標準namespace出力/固定API tag、caller close後DEBUG拒否。
3. 未bind DEBUG scrape拒否、STD空、取得0。
4. null/未知modeをbind/scrapeが拒否、取得0。
5. null constructor factory/registrar拒否。
6. factory Runtimeの元identity/一回、再bind拒否、close所有維持。
7. factory Error元identity/自動retry0。
8. factory nullをNPE契約違反として拒否、正常化0。
9. 既closed candidate拒否、registrar0、所有closeは明示だけ。
10. GC前registration Runtimeでpartial registry保持、scrape拒否、caller close一回。
11. GC保持後registration Errorで元identity、GC→registry close順、二重close0。
12. GC close失敗はregistry未close/成功偽装0、callerの明示再closeで残所有解放。
13. registry close失敗は未closed、明示再closeで解放/その後二重close0。
14. null GC callbackを拒否しpartial registry保持/元契約違反を正常化0。
15. bind単回/再bind拒否/STD未読/close冪等。
16. latch付きscrape実行中は同owner closeが待機、完了後close/以後DEBUG拒否。own workerだけ有限join、sleep/外部process探索0。

8668は既checked SDK10artifact/POM/Jarをnew-only coordinateへ置く。全prepared pin/親POM存在/不一致上書き0、public download0。source commit固定後8670正常六module→8672新16→8674新Main全line/method/class/branch100・PMD/CS/SB/negative→8676全1826物理/旧1825同byte/原1669同byte・依存五edge/owner trace→1809/scan。F/E/skipped/notrun PASS化0、除外緩和/旧exec転用0、障害修正前915/916。全command/env/OS/JDK/branch/source/日時/input/期待-実際/exit/coverage/hash/BUGは各manifest/result。着手時全16 UNRUN、formal1964-53/原190新受入0/工数null/QA051final/whole451/actualHOLD/元-v4-v5/原本等保持。
