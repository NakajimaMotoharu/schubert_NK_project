# NK-OPS-001 Artemis実効管理値 PT実行結果

PG235/PT-OPS-MQ-005～007は2026-09-24 JSTの選択runで3/3 PASS、failure/error/skipped0。実隔離ArtemisのCore management照会、属性欠落、全11実効値の独立変異、Diskの<90%境界、null/不正型/provider例外のredaction、借用session不変を確認。対象`ArtemisManagementReadinessClient` instruction222/222・branch22/22・line38/38・method9/9・class1/1、`ArtemisManagementReadinessException` instruction4/4・line2/2・method1/1・class1/1。選択commandは038、実行exit0、SpotBugs0。正式全reactor/Program証跡は未実施のため、この結果は未認定。関連新BUGなし。個別input/expected/actualは038とJUnit XML、正式証跡hash・source commitは次runの`evidence/manifest.json`で確定する。

この確認はSS321のbroker管理値の一部のみ。Journal復旧エラー、acceptor loopback、ACL、全Address設定、Queue閾値、Expiry purge、実Ops credential/production親起動、実NK CHR-L01は未完了。IT/STも未実施。
