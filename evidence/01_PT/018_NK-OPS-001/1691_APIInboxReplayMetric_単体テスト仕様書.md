# 1691 API Inbox replay metric 単体テスト仕様書

NK-OPS-001/P01809/C07/RD171 MON/ UI252/SS351§6・9/SS323全64layout/SS232 result/PG-D558/group1909。InboxReplayMetricRecorder constructor/record/detailedMetricsRequested。callerが既にreplayと認定したイベントの計数だけであり、再送・業務処理・Inbox検索・dedup/token保持や消費・DB/JMS呼出しは行わない。

DEBUGのcounterは`nk_inbox_replays_total`、labelは承認済64layout×12resultだけの768系列で事前登録し、STANDARDは登録/保持/増分0。未知layoutは英数字8桁として有効でも拒否する。registryはcaller所有。既同registry同metricの排他的assemblyはcaller前提で、ここでglobal所有を作らない。部分登録失敗の既登録meterはcallerに保持し、rollback・close・再試行で所有を偽らない。

| Test ID / method先頭 | 操作・独立期待値 |
|---|---|
| INBOXMET001 / inboxMet001 | SS323表から独立転記した64literalとSS351/232の12wire literal。直積768、名前/Counter型/label key2種/全pair/初期0、呼出768/close0 |
| INBOXMET002 / inboxMet002 | 各pair一回→全1、QSBREQ01/0200追加一回→2、増分769・系列不変 |
| INBOXMET003 / inboxMet003 | STANDARD全pair入力でも登録/保持/増分0 |
| INBOXMET004 / inboxMet004 | null registry/mode/layout/result・空/未知/小文字mode・未登録UNKNOWN1拒否、CONFIG_INVALID、既値/系列不変、両mode |
| INBOXMET005 / inboxMet005 | 第2登録でRuntime/Error、同一Throwable/呼出2/残meter1/close0、caller finally close1。例外文面読取も禁止したfixture |
| INBOXMET006 / inboxMet006 | increment前/後×Runtime/Error、同一例外・呼出1・実count0/1、補償/再試行/format/close0 |
| INBOXMET007 / inboxMet007 | 64並行callerで同pair64、別ownerの異pair1と他pair0、全768不変 |
| INBOXMET008 / inboxMet008 | foreign Gauge同名pairを上書きせず例外、同一meter/value7/close0、別fixture登録可能 |

expectedはSS表のliteral/直積/明示算術で、Production methodから期待値を生成しない。ResultCode.fromWire/LayoutIdはtyped入力形成だけ。既98を同sourceで必要再資格し当106/13suite・26Java/実21＋metadata1予定。旧98/別sourceBatch237-Web27・正常compile PT0を合算しない。protocol176classは依存として一部実行されるがAPI coverageへ合算せず、protocol PT成功やcoverage更新としない。

PG7625のmetadata preflightは元PG7614正常Jar SHA32889546…と全176class/debug・全protocol入力を照合済み。既M2 Jar SHA d28016d5…は174classでmissing2/different38、使用/上書き/install/download0。PT harnessだけ一つのsystem-scoped依存を資格済normal Jar絶対pathへ固定し、Production POM/元のcompiler-Werror/NullAway/SpotBugs/four100/全試験規約不変をXML tree比較と8負改変で検証する。後続fresh正常六compileのprotocol全176byteをこのJarと照合する。環境再現時は同protocol入力の正常compileを用意し新preflightで再認証し、pathだけ差し替えて既成功を流用しない。

PG7628host/7630独立/7632正常六compile/7634全Jar/7636trace/7638review/7640公開scan。source/run/OS-JDK-tool/日時/branch/command/終了/XML/input-output/CRC・四counter・静的・関連BUG/実hashを元manifestと1692へ記録。失敗/未完/skippedを成功にしない。全1643等の過去値ではなく当全1761Main/104src/92追加physicalを実測予定、旧1669byte不変を独立照合する。

開始3/5/9pp上限10/fresh27残73・元窓0/reset1793306748/event1909。新製造8/既98再資格/再認証/追加発見/手戻り/tool費を分離。正式1964/53・原190新受入0・工数null・QA051final/PTALT0・whole451/native/CHR・全actualHOLD維持、実VM/Root/DB/JMS/Backup/key/intent/permit/配備/ネットワーク操作0。

BUG-3881／YKT-2997。INBOXMET007の元の固定期待、8worker、64件、10秒、registry個別所有を保持。期限付き終了を共用し、二次失敗は一次を覆わない。現版の真正5件は[PG45494](evidence/PG45494-current-five-api-metric-fixture-owners/manifest.json)。実環境と正規全451は別。
