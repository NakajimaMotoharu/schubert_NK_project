# SCR009 Animation件数の過大申告の実行結果

2026-11-21、PT-WEB-SCR009-COUNT-001、WBS-P016-09/2-照合。宣言1／実0は期待どおりIllegalArgumentException、選択1件成功。失敗・エラー・スキップ・未実行各0。書式・Checkstyle・警告エラー化コンパイルは終了0。最初の準備ではjavac前に作業先のclassesを作らずコンパイルで終了1。準備を補った後の製品JVMは一度だけ。

現Main三物理のCRCはいずれも旧PG24476と異なる。旧WEB232を現ソースと照合した範囲はソースbyteと独立期待値。現runは新しいCRC、原exec、独立XMLで当境界だけを測った。実HTTP、P015-02、全451の条件は継続。

[PG41182の構成、実行、証跡hash](../018_NK-OPS-001/evidence/PG41182-scr009-animation-overclaimed-count-v1/manifest.json)
