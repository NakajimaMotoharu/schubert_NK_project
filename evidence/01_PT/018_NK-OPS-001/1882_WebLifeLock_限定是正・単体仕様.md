# Web停止owner private lock/待機表現・限定是正仕様

2026-10-25/PG-D641/primary WBS-P018-06、関連P018-05追加0。群P01806_WEB_LIFE_LOCK_REMEDY_V1、開始.5/1/2pp cap2固定、freshと元90下限はPG9244 quota receipt、下限＋2＋保全2<=90を確認。80大型抑制内の1881残同Web通知/解放経路だけ。

private final Object stateLockをresource-free ReentrantLockへ置換、install/close二synchronizedをlock/try/finally/unlockへ。既reentrant/非interruptible排他・二重install拒否・installed/stop/finishedの範囲を保持、caller公開monitorではない。holdUnknownIntervalの既InterruptedException catchは明示returnで一つの区間を終えるだけ、retainUnknown while(true)は不変更・UNKNOWNを成功/解除へしない。既例外範囲/割込みclear・provider/Hook/期限/Unit契約を変更しない。

新WLCLOSE004はcaller lifetime monitorを保持したまま自己Executorからclose完了することを独立future期限/停止値で確認。必要旧WLCLOSE001～003と計4/1を当source普通PT、旧成功確認でなく製品変更の影響回帰。actual install/HookDriver/TERM/holdUnknownInterval/retainUnknown/実Main/VM/Root/DB/nativeを実行しない。待機catch分岐は未実行HOLDのままmetadata/最小source/bytecodeで意図を照合しPTのPASSへ変換しない。

source固定→normal六一回→4普通PT→whole WebLifetime実coverage/三static→全1843 byte差/254owner/五arch→1883結果。対象三行の違反消去と他raw全行を残す、全Program PT/四100/451未完。BUG1743/YKT1494とYKT1493追加対象を先行登録・全対象/非該当/実source試験へ結合、原/v4/v5/原本等保持。fresh予算/安全停止条件まで通常小区切り停止なし。
