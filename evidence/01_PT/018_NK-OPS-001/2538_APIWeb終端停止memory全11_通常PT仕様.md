# 2538 API/Web終端・停止memory全11 通常PT仕様

2026-10-29/PG-D834予定/event2921/F03主・P01805/06は費用参照のみ追加0、開始1/3/6cap10。source0061d178c/normal13832/静的13838、Main/Test変更なし。

## PT_DEFAULT

元ApiTerminalCaptureTest全294/WebTerminalCaptureTest全294/WebRuntimeStopTest全191（正確な行数/hashはmanifest source固定、行数は成功件数でない）を丸ごと3/3/5選択。Test全body/fixture・Api/WebProcessMainの四引数constructor/main/run early return・TerminalCapture全source・FixedNativeCoverageCheckpointのcurrent/open分岐/FixedProfile parse全body/static定数・WebStop全source/SessionStoreException全sourceを確認した。

全ProcessMain.mainは必ず一引数overrideでrunが70を返し、禁止sourceは呼ばれればAssertionError。terminationはList追加のみ、defaultconstructor/System.exit/実サービスstartは非選択。Captureのopen/verify/close/runは既存memory Object/event又は意図的例外だけ、実owner/native採取ではない。System.err/handlerの変更はfinallyで復元する。currentJvm(null)だけは現JVM公開入力引数を読むが、固定host agentはwork/toolchain配下で、reserved `-javaagent:/opt/pgpt-tools-pg390/` に一致せずparseSelectedはempty→open即emptyを返す。NativeCoveragePrivateFile/固定agent照合/出力/StopHold.openには到達しない。別agentやnative flagsを追加しない。

WebStopはAtomicLongと手書Stepのみ、HTTP/worker/brokerは文字列。SessionStoreException.preserveFatalの既存単純IO/cause Error経路を呼ぶが、保留中Graph9（TemporaryInfrastructureException/WebStartupException）/cycle probe/未知providerを別callerで再試行しない。両wholeに既HOLD処理なし、部分抽出0。実DB/VM/Root/鍵/permit/intent/owned停止は不認定HOLD。

|既ID/whole|入力・独立期待値|
|---|---|
|API TAIL005/006:3|memory owner identity/null/IO/runtime/fatal、open/verify1/capture/verify2/closeの各故障と固定event prefix、正常時70一回、故障時terminationなし。primary/suppressed identityと固定stderr、lookup empty/failureの後続禁止。二つのrem006 prefixは完全FQCN#methodで一意化。|
|WEB REM005/006:3|上記の独立手書WEB literal/イベント列。固定expectedはProduction classifierを使わずTest内switch/List/identity。JVM argsはreservedではないというhost条件をtool固定。|
|NWEB STOP001～005:5|HTTP→worker→broker、30/28/25秒とdeadline0・超過の固定境界。UNKNOWNでは後続資源を保持しconfirmed phaseを二度解放しない。固定IOExceptionはcause/suppressedなし、runtime/lifecycleは再確認位置保持、direct/nested Errorは元identityで送出。並行実TERMは対象外。|

SYS002004/OPS009/UI212243253/SS311342343352・PG-D377/378/412、canonical owner API=P01805/Web=P01806。SHA・完全Test名・全input/dependency/環境/command/退出は13920元manifestと13922独立postへ保存する。Test自身のloopをJUnit件数へ増やさない。

command=`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg13920_api_web_terminal_stop_whole_eleven_pt.py`。JDK25.0.4/JUnit1.13.4/JaCoCo0.8.15、固定SDK/六jar/cleanENV/新javac-Werror、三suite11・単一exec/appendfalse。fixture map空、SharedReporter既12toolprofileを参照（新製品成功加算0）。13922で全三sourceの五executable/九abstract interfaceを完全inventory照合し、元XML・全source/Jar/sessionCRC/八型付き反例とcounterを測る。実factory分岐のmissを除外/人工到達/旧exec unionで埋めない。2539で実結果/残リスクを記録。

正式1964PT/53scope・17/190・工数null/QA051final不変更、障害は修正前台帳、全原本と二held工具保全。通常区切り停止なし、残10又は枠不明で保全。
