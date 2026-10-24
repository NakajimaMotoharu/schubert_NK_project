# Typed borrowed pool binding／HTTP 実行結果

1825/PG-D621/group2055、candidate Production `1e4f4049881c158760d285ce798dd3c4b6d0abbd`（未配備）、新Binding Main2/Unit2、既HTTP Unit2だけ変更。最終actual60/4 F0-E0-S0・元javac/JVM0/timeout0。**新22（POOLB各10＋HTTP020各一）、必要旧HTTP各19=38**を分け、新規60とは数えない。

|工程|公開artifact（evidence/provisional配下）|SHA256|
|---|---|---|
|旧source compile失敗/60UNRUN|PG8832-typed-pool-binding-six-compile-v1/manifest.json|f1aad824e88815f784b269ae4b13e33484ba47f7d64a97ba9bef680950e1ccd3|
|修正後正常six/PT0|PG8842-typed-pool-binding-fixed-six-compile-v1/manifest.json|067a5c46b02c9b99119cfc8837e83fa652ab7c8d3fa30e98eb67da3c4ac35e4d|
|当source元60/4|PG8844-typed-pool-binding-fixed-host-v1/manifest.json|fafa64a10e6cead62f1509ff9e607a15b3263601b2c6359428ce94820383a435|
|既六raw理由とcurrent XML結合|PG8845-typed-pool-binding-context-v1/manifest.json|cf3d5cf4bbf752478679b6d41e6c942b59f69474924a889858930582650229f3|
|当六Main実counter/静的|PG8846-typed-pool-binding-fixed-post-v1/manifest.json|365f0a72fdf78122ca14db3ce8808a9a2a421dbc7ac35f191a2ddbcc3926dc1d|
|全six/owner/typed read-only|PG8848-typed-pool-binding-fixed-trace-v1/manifest.json|0c6690234284064fc597c8dcce90721a951413a4600f34d789de10c0db4cc5cb|
|実SDK/adapter ABI＋original guard反例|PG8849-typed-pool-binding-guards-v1/manifest.json|dee908db5a9d7257ce7e97af5466104589c16e506740d0af2f172037ca39435e|

環境Java25.0.4+7-1-26.04-Ubuntu/Linux7.0.0-38-generic/amd64、Maven3.9.12/offline/dev-foundation。実command/UTC/branch/source/archive・inputs/六Jar/SDK-deps/fixture/tool/XML/log/exec hash/exitは各manifest。selected四suiteのみ60、ObservationTest二outerはfixture helperとしてfresh compileしただけで、その既@Testを実行・合格算入していない。

## 独立期待と実際

POOLB001～010は1825に一致。ctorはnull/未知modeでgetter0/series0、DEBUGでも初期値はunknown NaN・getter未読、refresh後API3/5/2/8・Web1/1/0/2と四getter順一回を確認。max0/各getter Runtime又はErrorではsnapshot empty/NaNへ戻し、真0/正maxは既知、元例外identity/後続getterと自動retry0、明示refresh回復を確認。last snapshotはfixture変更に追従せず、次refreshだけ更新、Integer.MAX_VALUEの正確なlong/double wideningとseries4不変を確認した。二own worker/first getter latchとsecond BLOCKEDで同一retained collectorの四read-publication直列化を確認し、解放後に両Futureを30秒内で回収した（sleep/実poolなし）。

POOLB008とMHTTP020はtyped public-interface fixture→新binding→実context Consumer→既full payload/HTTP Handlerの実部品接続。二観測の固定四値、ready1、200/UTF8独立byte長/二header/exchange close一回、invalid max後のNaN/empty snapshot・0偽装なし、SDKをcontextだけがcloseして借用beanのcontrol/credential/getTotal/lookupへ進まないことを確認した。fixtureはpublic Hikari interface proxyでありprivate reflectionでも実Hikari/Connection/JMX lookupでもない。期待は手書き数値/label/順/NaNと例外identity、production methodでexpectedを生成していない。source型interfaceに管理methodが存在しても本実装から呼ぶ権限を認めない。

## 当source scoped品質

新Binding2＋既collector2＋既HTTP Handler2の六Mainで、**line104/104・method18/18・class6/6・branch16/16全100%**、CRC不一致0/session一つPG8844-TYPED-POOL-BINDING、Checkstyle0/SpotBugs0/processing0。新Binding自身はstraight-throughであり、既collector条件を当60で実行してbranchを実測した。coverage除外/抑制/旧exec union/failed-skipped-notrun合格化0。Context全体や全1834Main・全451の100%ではない。

PMDは**raw6を保持・個別context評価済6・未分類0/適用違反0**。old API7372原cf76bd87、Web8132原f6d7ac40のcollector各三row（private lock一つ、Runtime/Error missing後same failure再throw二つ）だけを当source/rules同byteとcurrent XMLのPOOLB005/006/010へ結合した。旧PT/coverageを転用せず、新60から測定。8846 actual raw全属性/座標が凍結六rowに完全一致することを確認し、新規/未知警告を許容していない。PMD raw exit4を0と書換えず、六rowの理由/hashとcurrent結合をmanifestへ保存した。manager raw40/当XMLjoin pending19やglobal F03をこの六row評価で減らさない。

## BUG1719/YKT1470

元source70df45112の8832はSimpleMeterRegistryがAutoCloseableでないためAPI testCompile終了1/三Jar/60UNRUN（Mainは変更不要）。修正前起票し元archive/source/log/manifestを保持、1e4f40498で両Unitへ既同型Registry adapter（extends SimpleMeterRegistry implements AutoCloseable、super.close）を追加、九箇所ずつだけ置換した。初回SDK-dir誤pathのjavapはclass not foundであり確認成功ではない。PG8170のreused座標から実M2 core1.17.1 SHA9ca47dfa831409b40253c8dc98c17b9d3e050ebbde4d1543c5521dca2b95ad56を認証し、8849でSimple/MeterRegistry両宣言とpublic closeだけでAutoCloseableでないことを確認した。

8844起動前actual assertは両adapter/close転送/九owner/生SDK TWRなしを検査。8849は原host hash321ad03dの実assert二つだけをASTで取り出し、implements欠落/close転送欠落/生SDK一箇所/owner欠落/基底型誤りの五反例×二を全拒否（metadata検証、製品PT追加0）。実fresh classのjavapでAutoCloseableとSDK closeへの一回forwardも確認した。既Collector二Unitはadapter既存、HTTPは正しいContext TWRで非該当・既本文不変。新60/当六Main品質/全traceまで結合して限定CLOSED、修正commit1e4f40498、完了2026-10-25。

## Trace・費用・保留

8848は全1834physical/新Binding2だけ追加、旧1832はdebug含む完全同byte・原1667同byte、source A4/M2だけ。新二Bindingのprivate三field/public ctor-refresh-snapshot三API・非Closeable/read-only/no source acquisition、六role/六protocol/六field反例、五architecture edge0、旧HTTP19×2本文不変、owner223＋新4=227を確認。Hash/source rowsは証跡であり過去Core/manager成功をcurrent PTへ読み替えない。

開始3/6/10pp cap10・fresh45残55→終了fresh45残55/reset1793382075、共有丸め0≠専有0、N/T/工数/専有費null。usage1e461de65af2326ca576dc64e42ac4d18c8ed3e4fffbeae9cecd98cc7c240036（10-25 01:20:12→02:02:03JST、explicit新record0/完全性未証明）。元/v4/v5・開始見積・追加依存/手戻り1719・再認証・工具費を混同しない。技術新584→606Test/新Main31→33は異source値、actual60を原4222等へ合算しない。formal1964/53・原190新受入0/歴史17・QA051final/PTALT0/actualHOLD・原本等不変更。

own79942失敗1/41508-71067-91558-63638-61729各0の真正終端回収済、二重job/actual VM-DB-native操作0。旧8834/35/36/38は未発行UNRUN。8850公開scan/保存push後、callerの所有捕捉→context init→management→確認済stop後context closeのPG接続を進める。actual Hikari bean供給/VM/native/CHR・全451は未受入のまま、ソケット/権限/permit等を試行せず通常継続する。
