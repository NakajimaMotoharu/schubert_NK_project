# 管理Metric供給口 製造・単体テスト結果

1819/PG-D619/group2049、candidate Production `84ee59a95cf4911b40635240a29fe1d8c71cdaf5` 未配備、新Main0・変更Main4（handler二つ/manager二つ）とUnit二つ。両Handler actual36/2 F0-E0-S0（新017/018各二=新4、必要既001～016各16=32）。元36を全新規化せず、manager動的PTと実HTTP資格へ算入しない。

|工程|公開manifest（evidence/provisional配下）|SHA256|
|---|---|---|
|元Main compile失敗/36UNRUN|PG8774-management-metric-six-compile-v1/manifest.json|a355ee9cb9a03d95247df30f031b02782487e19248bb9cc18bf25568c5668a0a|
|修正source正常six/PT0|PG8784-management-metric-fixed-six-compile-v1/manifest.json|c2b565fd275d8a1bccd79cfa9ebf123809e3ad429190d37df2b6711caa244df7|
|元actual36/2|PG8786-management-metric-fixed-host-v1/manifest.json|48456d325d6acef25370360c544549bb171a412878dfb03f8363185780f22339|
|handler当2実四counter/静的|PG8788-management-metric-fixed-post-v1/manifest.json|082e7f9f143c8012fc3320d24eb88475b3ff2d236f9ed52f1960b2a38df7e1dc|
|全six/変更4/manager PG契約|PG8790-management-metric-fixed-trace-v1/manifest.json|b53058401d0e5a62d2df2e66f2291c5a9c32f6d2086f2be5a62afbf6c5f7de81|
|manager許可静的・PMD未分類40|PG8791-management-metric-static-v1/manifest.json|a90c75594c92df4ff73aa017a1a6c72eb152b97d32cdbc5df603b02e53990a47|
|PMD40のsource行由来だけ照合|PG8793-management-metric-finding-origin-v1/manifest.json|3b42b90552d2d8e6d91a3cfe805b2bda38398600dcb3028a701680d24f82cf36|

JDK25.0.4+7-1-26.04-Ubuntu/Linux7.0.0-38-generic/amd64、Maven3.9.12/offline/dev-foundation、command/日時/OS/JDK/branch/source/archive/input/actual six Jar・SDK/deps/tool/fixture/XML/log/exec hash/exitは各manifest。source間の旧counter/nativeを転用していない。

## 通常PTとして実測した範囲

handler二つだけ line50/50・method6/6・class2/2・branch8/8四100%、CRC不一致0・session1 PG8786-MANAGEMENT-METRIC、PMD/Checkstyle/SpotBugs各0/processing0/未分類0、七metadata反例拒否。除外/抑制/union/失敗合格化0。
新017はborrowed write後にclosed=false/calls0、手書きready1/UTF8独立長/二header、その後caller close一回/context再利用/null拒否。新018はready Runtime原identity/headers0/body0/未close・caller後close一回/context保持。既16各roleは変更後の必要回帰で全期待を保持、owned handleが一回closeするassertも追加した。Default HttpServer/server factory/start/stop/socket/nativeを呼ばず、memory exchangeだけである。

## PG・静的で確認した範囲（動的PTではない）

二Managerの新bind(context)はprivate Optional handlerをfactory.create前に捕捉、contextはcaller借用でinit/closeしない。this::readyを渡し、旧started/stopping/promoted/healthyからauthorityを分離しない。旧bindはOptional.emptyで既ready応答保持。新metrics rawpathのwrite委譲を除いてrespond本文、publicJson/promote/ready/stop尾部が旧sourceと同文面であることをsource guardへ結合した。内側writeをhandleへ替える二重close、型情報消失、ready authority変更、manager側初期化の八反例を拒否。javapで当source private handler/新bind二つを確認、ASMの五architecture edge0。これらはcode/metadata照合で、未知の拒否TestIDを特定したことやPT免除完了ではない。

manager二つの実静的は**Checkstyle0、SpotBugs0、PMD raw40/未分類40**、processing0、静的全合格ではない。PMDはDoNotUseThreads21、AvoidCatchingGenericException8、AvoidInstanceofChecksInCatchClause8、CompareObjectsWithEquals2、AvoidUsingVolatile1。8793は原XML/40raw順序/各package-class/pathとcurrent hashをjoinし、40全spanが変更前db9c16e03の行と同byteであることだけ照合した。既存行であることを非該当/合格へ読み替えず、F03の個別適用性レビューを次へ残す。raw XML/report hash・未分類40・8791終了1は保全する。新コードや品質への一律例外/抑制を加えない。

manager native/start-stop/borrowedcontext runtime所有/当sourceの停止budget/default providerは **UNRUN_HOLD**、coverage **null**。Root callerと実観測producerは未接続で別未完、manager供給口だけでDEBUG全catalog/鮮度や実起動を成功にしない。PT_EXECUTION_EXEMPT/代替確認完了0、PTALT0・F03 Root11/全actualHOLD維持。

## BUG1717/YKT1468とtrace

元fde3baa14はvar＋annotated wildcardがCAP#1へ推論され8774 Main compile終了1/三Jar/36UNRUN。先行起票後84ee59a95で二bindのOptional.<RoleMetricContext<?>>ofだけ明示、handler/expectedは同byte。元source/archive/log/manifestを保持。二Manager型guardの消失反例/実8784全six compile/8790当source port metadataと八所有反例により型障害を限定CLOSED、全manager品質/動的PTの合格とは別。oldbind emptyはconstructor targetあり、handlerは直接field、新Unit standardは<String>明示済で非該当。修正commit84ee59a95、完了2026-10-25。

全physical1832・追加削除0/変更4parentのみ、旧残1828/原残1667はdebug含む同byte。原1669のうちmanager二つが変更されたため、原1669不変とは報告しない。source/Unit差分は六ファイルだけ。旧221owner行のhandler四sourceを更新し、今回初めてmanager二sourceの所有を追加したため現223行（1819の予定221を着手中456で是正）、追加費0。current CRCはhandler二つのみでmanager未測定を含めない。

## 費用・保存・次

開始2/5/9pp cap10・fresh43残57→終了fresh43残57/reset1793382075、共有丸め0≠専有0、N/T/専有費/工数null。usage50f52e3f25a35ca6832a58ef76f95e1bfb92e1b397a8a40518bc25f22ee820e7、10-25 00:12:40→00:29:47JST・新explicit record0/完全性未証明。元/v4/v5・計画消化/追加発見・手戻り1717・source再認証・工具費を分離、見積減額=進捗化0。技術新564→568Test/新Main31のまま（異sourceで単一全体資格ではない）。正式1964PT/53scope・原190新受入0・歴史17/190/QA051final保持。

全own58134失敗1/92871-29748-95976-25246各0/71164静的1（未分類40）真正終端済。未発行8776/78/80はUNRUN、二重起動0/実VM-DB-サービス等0、原本・stash・keys/native証跡不変更。次8794scan/保存push→当40個別のSS/責務/独立根拠照合と許可済みF03作業、又はC07供給source/ownerの同経路PG/PTへ。受入待ち/小区切りでは全体停止しない。
