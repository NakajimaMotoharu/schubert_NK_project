# 487正式見積field・計測leaf追記訂正仕様

2026-11-01、BUG2192/YKT1939、Production6b53/HEADb10215e3。ADMIN群PG16925、一群0.25/0.75/2共有pp cap10を事前固定・freshused68残32、N/Tallocatednull。17件PG16926は未起動のまま記録是正、Source/Main/Test/期待/VM等変更0。PMO軽微指摘を現477/487と既3143/3465/3466・481/484の実物に照合し、返信待ち/費用再配賦を作らない。

対象元event=3554/55（3280・0.75/2/4）、3556/57（3283・0.75/2/4）、3558/59（3286・0.75/2.5/5）、3560/61（3289・0.75/2/4）、3562/63（3292・0.75/2/4）、3564（3295・1.5/4/8）。元仕様hash/元event line SHA/凍結値を明示し、正式groupStartEstimatePp(low/base/high)からcollector正式estimateAtGroupStartPpへ導出する。元拡張standardは既値の単なる名前対応で、見積額の変更/値引き/完成率ではない。

3554/55・3556/57のChild/Broker/Parent/Inspector固定byte・異owner/null/例外の限定PTは既03.02の部分対応を再利用。計測leafはP01803.02、canonical親P01803とFixedCaddy側04.02参照は別field/追加費0。3558/59は元計測04.02を維持し参照親03をwbsLeafIdsへ混ぜない。残三群はF03 leaf。どのleafもこの訂正で受入しない。03.01の実原本/FDと03.03終了依存・真正owner/同source全quality未完を維持する。

上書きせず現在時刻のCHECKPOINTへcorrectionOfEventIdsと正式fieldsを追記する。3558のLATE_CAPTURE、旧登録失敗/旧Source/run/元費用・時刻を保持し、事前成功へ書換え0。未知のPGPT専有費/N/Tはnull。hierarchyは481/484全recordから親情報を和集合し、同idの比較用rowが後から現れてもchildrenを消さない。Source/code/試験/VM等を再実行せず、六群/全十一eventの対応と次17件の正式着手が実証された分だけ工具有限scopeを閉じる。
