# シナリオ詳細の合成テンプレート例外型

NK-WEB-002、WBS-F03/2-2-b、UI223、SS313/354、PT-SCR-017〜024。固定のdetailメタデータと行、前後リンク、10000行・999音声の上限、既UIの出力、CSS、64並行描画、合成scratch書込みはPG14618の独立期待値を維持した。PG41542の4物理、共通MVCの31物理、資源3、Protocol現JARと唯一のlayout参照を実行前に照合。修正はbounded waitとscratch出力のchecked宣言のみ。

PG42826で包括SpotBugs1を確認。PG42828-v1は候補コンパイル・静的成功後、別fixtureを指定したためJUnit開始0／discovery終了1。BUG-3628を先行記録し、PG42828-v2はコンパイル済みの唯一fixtureのクラス名を確認して一回実行。JUnit8件が合格、失敗・エラー・skip0。SpotBugs0、Checkstyle0、PMD raw6は未抑制。元試験宣言を逆変換して旧入力・期待値とも一致。実行コマンド、JDK25環境、source、原XMLと公開XMLは [PG42828 manifest](evidence/PG42828-scenario-detail-template-current-v2/manifest.json)。BUG-3627/3628／YKT-2852の限定完了。新coverage、六製品全体、実Browser・CHRは別。
