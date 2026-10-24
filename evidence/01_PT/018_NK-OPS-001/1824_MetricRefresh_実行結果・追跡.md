# Metric refresh／HTTP接続 実行結果

1823/PG-D620/group2053、candidate Production `32041eafe19116bba7b90431f522371f0bcd8d53` 未配備。変更Context二Main/Unit四つ、新Main0。最終actual104/4 F0-E0-S0（**新16＋必要88**）、元javac/JVM0/timeout0。新MCTX027～033各7・MHTTP019各1だけを新規成果へ計上し、必要旧52/36を新規化しない。

|工程|公開manifest（evidence/provisional配下）|SHA256|
|---|---|---|
|元source正常six/PT0|PG8806-metric-refresh-six-compile-v1/manifest.json|43cbf64174401dde78c0e48fc7ecd3a43fee6f629755fe19ddc21945583bf334|
|元104/F2/exit1・失敗保持|PG8808-metric-refresh-host-v1/manifest.json|2548245c819e65f66e483722b572922baf76c3b2303bf19b5dd7c3af1b52f368|
|fixture是正後正常six/PT0|PG8820-metric-refresh-fixed-six-compile-v1/manifest.json|8107b7e202b684ba02a3fedda816ef40f3a4dcb1fbe7dd7fb785508b6d4c3d54|
|当source元104/4|PG8822-metric-refresh-fixed-host-v1/manifest.json|ef14dd6e0cff9a065771e0d06aa035623853a5ab5cc956c2c16e1c7624e99c33|
|実当四Mainのcounter/static|PG8824-metric-refresh-fixed-post-v1/manifest.json|bbacc38eab6910f114c63829eb68f65c435ec6cdf4b5da211a0289e8a0b805ca|
|全six/consumer/旧Test保持/owner|PG8826-metric-refresh-fixed-trace-v1/manifest.json|dbab6b7a10276bdd42a3a158fa92124b9a6c37908300116c20cc1937421e1b99|

JDK25.0.4+7-1-26.04-Ubuntu/Linux7.0.0-38-generic/amd64、Maven3.9.12/offline、dev-foundation。各実command/UTC開始終端/branch/source/archive・全inputs/六Jar/SDK/deps/tool/fixtures/XML/log/exec hash/exitはmanifest。Main四scopeはContext二つとHTTP Handler二つで、後二つはsource不変の必要consumerとして当runから測定した。**line198/198・method32/32・class4/4・branch59/59各100%**、CRC不一致0・session一つPG8822-METRIC-REFRESH、PMD/Checkstyle/SpotBugs各0・processing0/未分類0、七metadata反例拒否。旧exec/sourceの合算・除外/抑制・失敗/skipped/notrun合格化なし。全1832Mainや全451のcoverage100を意味しない。

## 独立期待と実際

027：DEBUGのstrong bindingへ一回ずつrefresh、setup7.5から手書き9.5→11.5、ready1→0/payload順序と同一metadata保持に一致。028：STDはsetup/refresh両未読・ready固定text/空bindingだけ。029：null callbackはctorで拒否し登録0、NPE正常化0。030/031：refresh Runtime/Errorは元identity、SDK/binding保持・自動retry/partial成功0、callerの次renderだけ元7.5で成功。032：意図的再入closeは既unconfirmed、callback帰還後stop再検査でrender成功を抑止しSDKを保全。033：finite own latch下の別thread closeは即時unconfirmed、callback解放後のrenderはIllegalStateException/新binding access拒否、最後caller cleanupでSDK closedに一致。MHTTP019は新refresh context→既HTTP Handlerの実部品接続で9.5/11.5とready1/0が二memory GET本文へ現れ、200/UTF8独立byte長/header/exchange一回close・caller binding保持に一致。production renderでexpectedを作成していない。

旧Context52とHTTP36は変更依存の必要回帰で全期待維持、8826は旧26×2本文prefixと旧18×2本文（新019部分だけ除いた全byte）不変更を確認。Callbackはpre-owned非resource metadata専用でありI/O/connection/JMS/worker/資源取得・context再入をしない契約。negative以外で再入せず、実Pool getterや観測全catalog/鮮度、defaultserver/manager/Root/native・停止budget成功を認定しない。

## BUG1718/YKT1469

元sourcec48bc1afbの8808は104中102成功/両033失敗、元終了1・XML/exec/log/source/archiveを保持する。fixtureがproceed未解放のまま同render lockを待つbindings()を呼び、workerの30秒awaitが先にAssertionFailedErrorへ終端（API818/Web819）した。closeだけがnonblocking契約で、getterは従来の直列accessという設計のまま。先行起票後32041eafeで二assert位置を解放/Future終端後へ移しただけ、新Main/独立期待/待機上限・latchは不変更。旧成功102を新sourceへ流用せずfresh六build/全104を実行した。

8822起動前の実使用guardが両033のentered→close→proceed解放→Future帰還→binding拒否の順を検査、同assertを解放前へ戻す二反例を拒否。既021は元からrelease→get→getter、032は同thread callback帰還後で非該当・既本文不変更。最終四scope品質と全traceまで結合し型や同期契約を緩和せず限定CLOSED、修正commit32041eafe、完了2026-10-25。

## Trace・費用・保留

8826は全1832physical/追加削除0、Context2だけ変更・旧残1830/原残1667同byte、二manager/二HTTP Mainも既byte不変。source差分六file/owner223全hash、private15field/Optional Consumer/公開ctor2-3引数と従来API・private lock/stop再検査・逆cleanup、四role/八sampler/四field反例・五architecture edge0。既init/close本文同byte、metadata callbackをDB/ネットワーク権限へ拡張しない。manager旧raw40（21context/19当sourcePT-XML join待ち）の過去source84の記録を本source成功へ変換せず、動的/native・global F03受入0を維持する。

開始3/6/10pp cap10/fresh44残56→終了fresh45残55/reset1793382075、共有観測1pp/専有費不明（他chat含む）。usagebd78061f0beb791dc413ad911c17fa7d3c53798a7819fc0fb139819eb97cf993（10-25 00:47:51→01:20:12JST、explicit新record0・完全性未証明）/N-T/工数null、元/v4/v5/見積と手戻り/再認証・工具費は分離保持。技術新568→584Test/新Main31のまま（異source部品値、全体PT104+4222等へ算術合算しない）。formal1964/53・原190新受入0/歴史17・QA051final/PTALT0/whole451・全actualHOLD/原本等不変更。

own86548正常0/37906失敗1/9421-7537-71635-87093各0の元終端回収済、製品job二重起動0。未発行8810/12はUNRUN。8828公開scan/保存push後、API/Webのtyped borrowedPool binding→refresh/context/HTTPへ同経路PG/PTを継続し、その後actual caller PGの必要依存を解消する。小受入/commit/報告で全体停止しない。
