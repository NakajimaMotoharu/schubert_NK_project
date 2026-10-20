# 1240 private monitor全参照の適用性調査（PG未着手）

source682a4b99eb0b95bcd4f1cd276fea75b5f2e62e3b、WBS-F03/event1419、調査開始.25/1/3pp。現在の未点検monitorは154/49source。PG5926全体の元source/Main/Testは固定し、本調査はProduction method/サービス/VMを実行しない。

SourcePrivateMonitorInventoryはjavac parse/analyze/-proc:none/-implicit:noneで、inline初期化されたprivate final java.lang.Object fieldをsymbolで列挙し、全参照が当this/暗黙thisのsynchronized expressionだけの場合に候補とする。alias返却/borrow/引数/待機通知/holdsLock/他instance資格参照は候補にしない。constructor供給lock・非final fieldも対象外。抽出は適用性factでありPGの是正・仕様適合・PT成功そのものではない。

独立fixtureはalias/escape、wait、他instance参照、factory供給、非finalを除外し、同this/暗黙outer参照/nested classの正しいownerとsource spanを確認（二unit/compile0）。試作初期のunused json importはfixture実施前pyflakesで検出・除去、最初のMain実適用前に解消した。Production障害/PT成功へ加点0。

5932/元29671実0：全851 Main/1666実classpathに固定し、inline private-final field48、eligible45、monitor129箇所/44sourceを得た。private manifest **7c96fbfec855589ceb316267c60b7fbb50dfde9b1db0f672e7f7338f561fe786**、helper/fixture/command/全source/class・型factはWorkPG379/pg5932-private-monitor-facts-v1に保存。Mainのprivate反射/Unsafe参照も検索結果0。未点検154とのsource/line/span対応、全critical body保持、statement親context（条件/labeled等）・field構築と所有契約をさらに確認してからPG対象を確定する。

単純候補外25：OwnedOutboxDispatcher/WebHttpAdmissionのwait/notify/holdsLock依存十三、BackupUnitStartClient/MaintenanceUnitStopClientのfactory共有lock八、WebHttpServerのresult.lifecycleLockという他instance資格参照を含む全四。保留は別途の設計/所有/並行分析が必要で、rawを削除せず未完を維持する。これらを新sourcePGの成功やレビュー代替へ一括加算しない。

次は親statement contextを含むsource変換条件と個別Test/現在coverageを確認し、PG対象確定・先行BUG/YKT/PT仕様→元PG5926真正結果/独立資格の保全後に限り実装する。129候補を完成計上0、残999/raw1544/pending545・正式1964/53/17-190/工数null/QA051final・原v3v4不変更。安全条件不明の実VM/current/原本/鍵/permit/failed-cohortは保留、通常小調査で停止しない。
