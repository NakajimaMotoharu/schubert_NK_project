# 1723 Duration極小/MAX混在 追加品質単体テスト仕様書

group1947/NK-OPS-001/P01809/C07/RD171 MON005006/UI252/SS351/PG-D568570補強。DBTIME009・MQTIME009を追加し、既元製造8ずつとは別の**追加品質oracle**として計測する。Production Main/既期待値を先に変更しない。

入力は独立固定二順序 [0,1ns,MAX,MAX,1ns] と [MAX,MAX,1ns,0,1ns]。DBは既Query二×Outcome二、MQは既LGNREQ01/WLGEVT01×Outcome二、各組合せfresh自己所有Registry/固定Clockを使う。いずれもcount5/sum1.8446744073709553E10秒/max9.223372036854776E9秒、既五有限bucket .001/.01/.1/1/1.5のCDFは小さい三入力（0/1ns/1ns）から全3と独立算出する。p95の数値精度・実exporterや実時間は未受入のままで、この試験をその受入へ代用しない。

SDK内部のdynamic range調整・最初の大/小観測からの順序依存とoverflow/dropを検証する。scalar自体が合法でもprovider故障を許可する仕様と、既固定bucketの数学的期待値を混同しない。failed/flaky/skipped/not-runを合格にしない。障害が再現すれば、修正前に実最終915/916番号を確認して起票し、元source/run/SDK出力を保全した上で合理的な内部是正を行う。期待値を実装結果へ合わせて変更しない。拒否PT/Root/実環境の試行・再試行ではない。

予定は新2＋必要既API162を当164/20で実行し、同sourceの四100/CRC/static・正常六compile・全1788physical/135delta-119physicalを検証する。今回Mainは不変更、前sourceのWeb77/Batch261/正式1964を合算せず、二Test fileの編集anchorを明示する。元追加製造/追加品質/既再資格/発見・手戻り/tool費を分離する。1724結果へsource/run/環境/command/exit/期待値/実際/counter/関連BUG/hashを結合する。

開始0.5/1.5/4pp上限10/fresh12残88/reset1793382075・PG7960 fresh receipt→event1947。原-v4-v5/旧markerlast27区間/共有累積・専有N-T/工数null/90再基底化0、正式/原190新受入0/QA051final/PTALT0/whole451-native-CHR/全actualHOLDを維持する。SQL/DB/MQ/時計/VM/Root/配備/鍵等の実操作0。
