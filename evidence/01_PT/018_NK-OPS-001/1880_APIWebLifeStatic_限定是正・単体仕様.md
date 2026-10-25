# API/Web停止通知ownerの静的是正・限定単体仕様

2026-10-25/PG-D640、1879の具体是正。P01805_API_WEB_LIFE_STATIC_REMEDY_V1、primaryP018-05/関連P018-09追加0、開始0.5/1/2pp cap2固定。fresh値と元90下限はPG9230 quota receipt、下限＋2＋保全2<=90を確認。80大型抑制内の同通知/解放経路の最小是正だけ。

API installedのvolatile booleanをAtomicBooleanへ、install既成功後set(true)、close既stop後getAndSet(false)で一回claim。API/Webの既shutdown-in-progress ISEだけcatchは明示return、必ず既finally finished.countDownへ入り、例外範囲/Hook/System.exit/provider ownership/期限を変更しない。ignored rename/comment allowlist/抑制/無意味assertは追加しない。RD171/UI252/SS312313342351/451、元vendor pin/JDK read-only根拠1879。

影響回帰は同source API LIFEBUDGET001～010の10とAPIOBSBOOT009の1だけ、旧sourceを現在資格へ移植しない。新WebLifetimeOrdinaryCloseTest WLCLOSE001～003は未installのstop/close二回、failed awaitのliteral IO、null境界/自己Executorから既finished shutdown returnを確認。native HookDriver/install/TERM/実Main/実DB/VM/Root/配備は0/HOLD。新Web3だけを新IDに計上し必要旧11を重複計上しない。

source固定→normal六一回→selected14/3→二Lifetime source unit全実counter（未実行anonymous/Hook分岐・missed保持）＋当三static→全1843/旧byte/当sourceowner/trace→1881へ。対象raw違反消去を確認しても全Program PT/四100/451/actualは未受入。BUG/YKTは修正前起票、既API/Web全対象と非該当・元失敗/新証跡を結合し当scopeだけ再試験する。元/v4/v5/原本等保持・通常小区切り停止なし。
