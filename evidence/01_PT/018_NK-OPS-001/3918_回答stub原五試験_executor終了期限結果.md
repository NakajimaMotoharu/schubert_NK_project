# 回答stub原5試験のexecutor所有・再試験結果

G03.05主/P01202関連追加費0、REWORK開始見積1/4/8pp・cap10を保持。Production Main7aed不変更、実Test/sourceは`9738ad03ae41b4c3a098ad77b7d2ed0b29f6b476`。BUG2559の一executorだけをTWRからfinally shutdownNow→awaitTermination10秒assertへ変更した。既timed invokeAll5秒と全64時刻/clock回数/空回答/identity/null/equals/赤字化の期待を保持。返却Future.get()はterminal後であり別の無期限wait障害にしない。gfmtの公開固定文字列分割も逆変換すると元Git blob全体に完全一致（PG24870）。新Test設計/fixture切出し/製品Main変更0。

最初の工具準備は4回の失敗（import1/lint1/引数契約1/旧classpath artifact欠落1）、全て製品compile/試験開始前。BUG2560～2562へ修正前保存し、元成功prepareは再演しない。legacy互換patchを続ける方針を是正し、最近の成功24394のConsole方式・明示最小CPへ変更。旧normalにclasspathファイルを加えず、capture guard/argvを偽装しない。新PG24898 preflightと現entry sourceを正とし、旧PG24888/prepareのunitTool記述は歴史記録として保持する。

PG24872でtestのみjavac release25/-proc:none/-implicit:none/-Xlint:all/-Werror成功、JUnitConsole1.13.4で元whole5を一回実行し終了0、全5成功/F/E/S/aborted/notrun0。外側180秒・専用cwd/tmp、ja/JP/Asia-Tokyo、class-initと単一Jacoco sessionを保存。実行前にsource9738を通常push。Mainは既normal APIJar、SDKはConsole/JSpecify1.0.1/JaCoCo0.8.15/JDK25.0.4でactual hashをpreflightへ固定。compiler・unit・coverage・execinfo・classinfo各終了0、確認目的の旧成功PT再演0。

PG24874は別Pythonで全XML5のmethod/source集合・成功、unit XML由来のOS/JDK/locale、独立固定公開出力、二Main SHA/実CRCと一session、全4保留型の初期化/true-probe0、sourceとdependencyの実byteを照合。9種類の型/失敗/欠落/source/CRC/B0偽100/偽終了/出力の反例を拒否した。StubAnswerProvider・AnswerResult各L5/M2/C1/I21とI19、miss0。両Sourceにbranchはなく自然B0=N-A/null、strict非空四gate1で全Source四100とは記さない。AnswerProviderは宣言型でCode受入へ加算しない。標準record filterは無変更、手動除外なし。

PMD raw5（Test並行4/明示finally resource1）は全件個別適用性を確認し適用違反0、processing0/Checkstyle0、suppression追加0。Main staticは未変更同byteの22086六module0を参照し不要な再実行なし。PG24876は2560～2562の全対象と正規入口/既runtime/旧snapshot不変を照合。製品IO0、Testだけの新cwd固定公開txt一件。実DB/JMS/HTTP/認証/session/token/key/Graph/Root/VM/native操作0、旧原本/保全物/鍵/stash7/Currentbaselineに変更0。

BUG2559は限定再試験完了、全YKT2177はOPEN。他117の構文候補はreceiver未確認でありFuture/障害と推定しない。unique520/Java416、候補114/pending12/whole93暫定、新規leaf/Source登録0、正式1964PT/53scope、工数率null、QA051/全HOLDを維持。IT/STの完了ではない。

|証跡|path|SHA-256|
|---|---|---|
|元owner|`evidence/01_PT/018_NK-OPS-001/evidence/PG24864-stub-owner-before-v1/manifest.json`|`a46ce76811f4857cb460b3f8ed00a89490bea30fa495202827001188dc3332f9`|
|format/static元|`evidence/01_PT/018_NK-OPS-001/evidence/PG24866-stub-owner-prepare-v1/manifest.json`|`247ca39b147d5560b6d05b03044d880b1ddfd71720af1a0a6f4da60524c47f8f`|
|static適用|`evidence/01_PT/018_NK-OPS-001/evidence/PG24866-stub-owner-prepare-v1/static-applicability.json`|`2e4d1dcad7e7ca44410ecb8e6529a78023d8f662475e520864644c99e404504b`|
|元assertion不変|`evidence/01_PT/018_NK-OPS-001/evidence/PG24870-stub-owner-whole5-preflight-v1/manifest.json`|`a349ff3482c3ec47f98504863534432cfecb32be4aee16cbf80161d85ecced7f`|
|現Console事前条件|`evidence/01_PT/018_NK-OPS-001/evidence/PG24898-stub-current-console-preflight-v1/manifest.json`|`f3562429a4e37e7df00060ef76bd027d764147698507f0c513a0ba663668fb5f`|
|真正終端|`evidence/01_PT/018_NK-OPS-001/evidence/PG24872-stub-owner-original-whole5-v1/manifest.json`|`70eccff09e6d3b349c935d4eda3e1b5eae8eb3df236e2119c40f51d74203f825`|
|独立|`evidence/01_PT/018_NK-OPS-001/evidence/PG24874-stub-owner-whole5-independent-v1/manifest.json`|`0e0156450a4af1b672e09b68584522f2d779d3e93abf6de28eb2a47168849d78`|
|工具横展開|`evidence/01_PT/018_NK-OPS-001/evidence/PG24876-stub-owner-tool-recurrence-post-v1/manifest.json`|`95232b26e5d1560eb8fad70b4fcb24121764b5260ac669118ed2317397ed9b83`|

実command：`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg24886_stub_owner_whole_five_pt.py`、checked lint0/body0。独立は830_stub_owner_whole5_independent.py、横展開831、いずれも終了0。全command/PID/実時刻/終了・実XML/coverage/execinfo/class-initは新私有`work/pgpt-runs/PG379/pg24872-stub-owner-original-whole5-v1`。公開は独立結果のtestcases.safe.xml/coverage.xml/固定txt/execinfo.safe.txtと各manifest。Source本文やraw private logを新たにGitへ複製しない。
