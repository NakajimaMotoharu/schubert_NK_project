# 1723 Duration極小/MAX混在 追加品質単体テスト仕様書

## BUG1678是正後補足（元oracle・開始見積り不変更）

BUG1679補足: source ded75/PG8006は174/21 FES0だがSpotBugs constructor継承安全性1件でverify1、PG8010は六compile0/PT0。Production registryをfinal化し、package-local ExactDurationSupportの空marker契約と共通factoryを使用する。三fault fixture/ProbeはSDKを直接継承、Production finalを破らない。追加markerはfields/methods/初期化0を非初期化javapで確認し全physicalに保持、counterへ架空加算しない。更新後43Java/実36＋metadata2/physical38、六全1791・138source/122追加physicalを予定。元009期待値、EXDUR十ID、群開始見積・原失敗を不変更。

元source0b78/7962は164/20中DBTIME009・MQTIME009が失敗、各小bucket期待3対実1、verify終了1。同source7966正常六compile終了0/PT0は別証跡として保持。修正前BUG1678/YKT1429起票済み。

ExactDurationMeterRegistry専用EXDUR001..010を追加し、必要既164と合わせ当174/21を予定。001:各五境界の±1ns/equal全15入力、CDF2/5/8/11/14・sum7.833/max1.500000001。002:元009と同独立二極端順序、CDF3/count5/同sum-max。003:負/NaN/±無限/MAX超の6入力で更新なし。004:empty/保持snapshot配列改変・後続観測と非alias。005:scale/unit/histogram/client-percentile/boundary異常をfactory拒否。006:汎用registryはSTANDARDのみ、DEBUGは両recorderで拒否。007:他summary/counterの元SDK動作と所有。008:null構成/clock拒否・durationのclock未読・default構築。009:四worker各64入力1秒と並行128snapshot、終了count/sum256/max1/CDF0/0/0/256/256、全future期限内回収。010:補助gauge factory同一例外・非所有close/再試行なし、le gauge値1。

独立期待値は上記literal/数学的CDF、Production関数でexpected生成しない。二元009の期待値と旧正常数値oracleは不変更。未要求かつ未受入のSDK phi補助だけ削除し、primary+五leの6meter契約へ明示更新。専用registryの二classとMain二/Test三の変更を別trace、実DB/MQ/clock/Root/actual exporter操作なし。対象class/methodはEXDURの名前と一意対応、null契約・全condition・静的解析/四counter・公開scanを当sourceで確認する。coverage未達や試験失敗は合格に含めない。

group1947/NK-OPS-001/P01809/C07/RD171 MON005006/UI252/SS351/PG-D568570補強。DBTIME009・MQTIME009を追加し、既元製造8ずつとは別の**追加品質oracle**として計測する。Production Main/既期待値を先に変更しない。

入力は独立固定二順序 [0,1ns,MAX,MAX,1ns] と [MAX,MAX,1ns,0,1ns]。DBは既Query二×Outcome二、MQは既LGNREQ01/WLGEVT01×Outcome二、各組合せfresh自己所有Registry/固定Clockを使う。いずれもcount5/sum1.8446744073709553E10秒/max9.223372036854776E9秒、既五有限bucket .001/.01/.1/1/1.5のCDFは小さい三入力（0/1ns/1ns）から全3と独立算出する。p95の数値精度・実exporterや実時間は未受入のままで、この試験をその受入へ代用しない。

SDK内部のdynamic range調整・最初の大/小観測からの順序依存とoverflow/dropを検証する。scalar自体が合法でもprovider故障を許可する仕様と、既固定bucketの数学的期待値を混同しない。failed/flaky/skipped/not-runを合格にしない。障害が再現すれば、修正前に実最終915/916番号を確認して起票し、元source/run/SDK出力を保全した上で合理的な内部是正を行う。期待値を実装結果へ合わせて変更しない。拒否PT/Root/実環境の試行・再試行ではない。

予定は新2＋必要既API162を当164/20で実行し、同sourceの四100/CRC/static・正常六compile・全1788physical/135delta-119physicalを検証する。今回Mainは不変更、前sourceのWeb77/Batch261/正式1964を合算せず、二Test fileの編集anchorを明示する。元追加製造/追加品質/既再資格/発見・手戻り/tool費を分離する。1724結果へsource/run/環境/command/exit/期待値/実際/counter/関連BUG/hashを結合する。

開始0.5/1.5/4pp上限10/fresh12残88/reset1793382075・PG7960 fresh receipt→event1947。原-v4-v5/旧markerlast27区間/共有累積・専有N-T/工数null/90再基底化0、正式/原190新受入0/QA051final/PTALT0/whole451-native-CHR/全actualHOLDを維持する。SQL/DB/MQ/時計/VM/Root/配備/鍵等の実操作0。

## EXDUR011 拒否後に別workerから記録できること

BUG-3734、YKT-2929、WBS-F03/2-2-b／P018-09、RD171／UI252／SS351 §6。前提は空の自己所有Micrometer registry、固定clock、正規の5境界。ExactSummary.recordにNaNを一回渡して拒否を確認する。続いて別のテスト所有workerが0.1秒を一件記録し、takeSnapshotを5秒以内に返す。独立期待は件数1、合計・最大値0.1秒、CDFは0/0/1/1/1。NaNの算入、失敗後の排他残存、snapshotの不整合を検出する。workerにはvirtual threadを使い、finallyでshutdownNowと10秒の終了確認を行う。入力は固定値と自己所有registryのみ。

収録範囲は元EXDUR001～010およびEXDUR011。元10件の期待値は維持する。Java25、Mavenローカル固定依存、選択Test ID、実行commit、NullAway・書式・Checkstyle・PMD・SpotBugs・単一exec四指標、実JUnitの終端は再試験manifestに結ぶ。全製品の正規包装・全451は別の条件。
