# 純粋表示28methodの境界・null・所有・並行PT結果

仕様2069/群2402（開始1-3-7pp/cap10）。source65bcd70a1dec722bd70be03468d9343142a7e789、Main21d/全1843不変。既normal10434/静的10432・元全token10436は照合参照し、成功確認だけの再実行0。三Testの既28method（Scenario12/Animation8/Music8）を原006/016/020仕様のTest IDと完全一致で束縛した。新Test ID0、原4222/旧source全体は再実行していない。

|公開run manifest|真正結果|SHA256|
|---|---|---|
|PG10450-pure-view-boundaries-preflight-v1|終了0、原仕様/source/28catalog/三suite/15完全Main class・14定数proof固定|19eaafbc5948d221c4ef47024daaef1ee39240e6d1aa4fb060bd7afda295553a|
|PG10452-pure-view-boundaries-host-v1|終了0、28PT/3suite、F/E/skipped/aborted/container失敗0|245079d2121878f0039794c6eecfe3ebc5b0a965ee457788f4138c974dbdf192|
|PG10454-pure-view-boundaries-post-v1|独立終了0、元XML/summary/source/class CRC/session/held probe・classload0|e36efc95cb2d4c81bf79f6b68e5527ee91d655cc5de728f16372f18e4bbcbb5d|

各manifestは `evidence/provisional/<run>/manifest.json`。完全command/OS/JDK/tool/dependency/時刻/終了code/input/actualは各invocation・stages、元XMLは10454/xml、期待値は原三仕様・2069。実行は `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg10450_pure_view_boundaries_preflight.py`、同10452_host、10454_post（各実名は工具path参照）。Linux7.0.0-38/JDK25.0.4/JUnit1.13.4/JaCoCo0.8.15、当新工具pyflakes0。Product/Main/Test source変更0、元八DB依存enum Test/Root/VM/DB/key/実サービス操作0。

新sessionPG10452-PURE-VIEW-BOUNDARIES、start1793007465380/end1793007467524ms。旧四methodだけのexecや旧b98成功との合成0、同run28件を一度だけ計上。前群当source四件と重複する四件は累積32件へ算術加算しない。新たに当sourceで確認できた条件は残24method、全scope/newAcceptedは0。

## 完全15Main class counters（covered/total）

|class|Line|Method|Class|Branch|
|---|---|---|---|---|
|AnimationListViewModel|49/49|9/9|1/1|40/40|
|AnimationListViewModel.Row|7/7|4/4|1/1|0/0（非適用）|
|AnimationListViewModel.Video|16/16|7/7|1/1|8/8|
|AnimationMenuViewModel|19/19|8/8|1/1|4/4|
|GameListViewModel|12/12|5/5|1/1|2/2|
|GameListViewModel.Card|9/9|5/5|1/1|0/0（非適用）|
|MusicCategoryViewModel|27/27|7/7|1/1|14/14|
|MusicCategoryViewModel.Card|9/9|5/5|1/1|0/0（非適用）|
|MusicSectionViewModel|31/31|8/8|1/1|14/14|
|MusicSectionViewModel.Card|9/9|5/5|1/1|0/0（非適用）|
|RouteListViewModel|16/16|8/8|1/1|2/2|
|RouteListViewModel.Card|12/12|7/7|1/1|0/0（非適用）|
|ScenarioFileListViewModel|23/23|10/10|1/1|6/6|
|ScenarioFileListViewModel.Card|13/13|7/7|1/1|0/0（非適用）|
|TopBarViewModel|8/9|5/6|1/1|0/0（非適用）|
|測定15合計|260/261|100/101|15/15|90/90|

14classは適用counter未網羅0、TopBar.toString一method/一lineが残る。0/0は100%実測と記載しない。Main1843不変・非対象Test1956不変、元source比較のphysical差六/三SourceFileに限定。原static raw六は既10436の所有Test executor文脈根拠で保持、CS0/抑制0/全F03未受入。

本runは純粋表示factoryのみで実画面HTTP/Browser/CHR/native/全451/IT/STの完了ではない。WBSのtemplate/HTTP・exit依存未照合を残すため正式1964/53・個別17/190・工数null不変。QA051 final/安全HOLDは維持。

fresh used4→4/reset1793599188、共有丸め0≠専有費0、N/Tnull・usage007c93c6。元見積り/v4残・費用/追加確認を区別する。次はTopBar診断文字列の独立PT不足を既実装・既Testの依存へ照合し、必要な実装済み試験の不足だけを修正前に台帳登録する。拒否操作の代替経路や元DB依存Testのfixture回避へ展開しない。
