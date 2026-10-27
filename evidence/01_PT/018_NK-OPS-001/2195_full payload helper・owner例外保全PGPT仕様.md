# 2195 full payload helper・owner例外保全PGPT仕様

NK-OPS-001/WBS-F03、群FULL_PAYLOAD_HELPER_OWNER_GUARD_PGPT_V1/event2556、開始使用33/reset1793599188、原2/5/9共有pp cap10。BUG1910/YKT1659/PG-D704、RD171/UI252/SS351/411・1812/1833/2194、sourceBefore d4b5507ba。

F03-FULLGUARD001：三fullOwnerに返却成功flag＋finally未移転close、成功時だけcallerが保持。API/Webfull012はowner取得直後の外側plain try/finally（元明示close oracleを保持し-Xlint:try違反を避けるためTWRにしない）、四full011012 executorにTWRを追加、元release/shutdown/await30秒・future30秒・全oracle/close順を保持。元API25/Web25/Batch36＝86methodを逆全tokenで保持、Main/上位不変更。fullProbeへclose回数の独立fixture instrumentationだけ加える。

002：新APIFULL013/WEBFULL013/BATCHFULL013はfresh Probeを一回close→fullOwnerへ渡してbind拒否、固定診断standard metric registry closed・追加cleanup一回でclose計二回・scrape0・closed=trueを検証。期待は取得前の独立literal/count vector、Productionでexpected算出0。probeはplain finallyで保全、追加closeはassertion後。元成功/helper成功・三新失敗辺を同一source/一JVM89/三suiteで通常実行、metadata負例は製品件数と分離。

003：normal六module package/Enforcer・format・NullAway・Werror/PT0→閉89 catalog/日本語JVM・単一exec。own memory SDK/fixed scalar/自JVM公開MXBean・GC listener/元有限workerだけ、外部HTTP/DB/JMS/VM/Root/鍵/強制GC/保留二工具・Graph9/deferred8の抽出0。JVM240秒、元latch/worker/future期限保持、自動extension/parallel/package discovery無効・空own CWD前後不変。API/Webはcustom→standard/旧ready・診断、Batchはsort/固定label/type/borrowed所有/独立full goldenを保持。既86は変更影響の必要回帰であり新Test IDは三つだけ。

004：当三Test PMD/CS/processing実測を保持、未分類を抑制/ゼロ化しない。一execのCRC/sessionを完全API467/Web358/Batch645へ個別読取し対象payload/text三Main四counter・全artifact未達を区別、全1843Main/他Testbyte・当三SourceFile物理差を照合する。元担当cost/trace/歴史/予算/全WBS auditの真正状態・command/env/exit/hashを2196へ結合、YKT1659の未知を自動完了にしない。正式1964-53/17-190/工数null/QA051final・全安全HOLD維持。
