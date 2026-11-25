# 比較工具の合成並行fixtureでの診断保持

NK-CHR-001、SS354/355、UI264、WBS-P020-01.03/2、BUG-3863／YKT-2997。

| 対象 | 独立した期待値 |
|---|---|
| 定義・baseline数値・evidence・metrics・相関投影の既5 | 元の正常値と異常原因をそれぞれ保持。2 workerとFuture 5秒、終了10秒。既入力と期待値を変更しない |
| PT-CHR-WORKER001 | JDKの代理executorが終了不可または割込みを返す。cancel、同10秒の待機の順。一次例外を同じ実体で保存し、終了異常1件を抑制。割込み時は元causeとthreadの割込みを保持 |

合成JSONと公開定義のみを使用する。実Current/NK、実Browser、DB、実ログ、QA-051の最終受入は別。実行command、入力hash、終了、局所coverageはPG45408のmanifestを参照する。
