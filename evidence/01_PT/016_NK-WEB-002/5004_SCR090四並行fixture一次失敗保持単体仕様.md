# SCR090四並行fixtureの一次失敗保持

NK-WEB-002、SCR090、UI221/222/226、SS313/314/354、WBS-P016-24/2、BUG-3909／YKT-2997。同じ4工程テストをメモリ内の固定Servlet/Callback入力だけで実行する。二thread、元2／8個の独立入力、Future5/10秒、終了確認10秒を維持する。

| 方法 | 既存独立期待値 |
| --- | --- |
| ErrorControllerPortTest.sharedControllerHasIndependentConcurrentRequestAndModelState | 403と405、各固定IDと画面モデルが混線しない。 |
| ErrorDispatchRestorePortTest.eightConcurrentRequestsKeepRestoredAndAnonymousAttributesSeparate | 8個の合成表示の認証有無と二alias、callback一回。 |
| ErrorDispatchRouterPortTest.concurrentRoutesKeepEightSuppliedContextsAndCallbacksThreadLocal | 固定callback順と各workerコンテキストの独立・解除。 |
| InternalErrorRouterPortTest.eightOwnedTasksKeepRequestsCallbacksAndEmptyContextsIsolated | 8個の半数ずつを元通りERROR／通常callbackへ送り、空contextを引き継がない。 |

元PG28022・28110の期待は変更しない。現Web共通workerの一次例外／終了例外の独立証拠はPG45598。現型、固定依存、実行環境とXML、単一execの測定対象、現終端を5005に記録する。実セッション、実HTTPS、実DB/MQ、実認可と全体451は別条件。
