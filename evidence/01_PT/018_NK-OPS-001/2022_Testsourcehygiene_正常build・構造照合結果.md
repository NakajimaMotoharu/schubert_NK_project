# Test source hygiene・正常buildと構造照合結果

工具lint補足：全新Pythonのpyflakes確認時、10020 patch exporterの未使用Path import一件を検出（製品Main/Test/候補/正常buildの欠陥ではない）。f976保存後に当一行だけ除去し、既manifestの元工具hash/原lint1は履歴として保持、emit/候補/build/PTの確認再演はしない。新lint結果と当工具hashは次保存単位へ記録する。

2026-10-26 08:04 JST、2020仕様/2021候補・反映/群2279/WBS-F03、source5012c53265d8d8d789ea2a3edf0b63fa45853a6a/dev-foundation/origin一致。Main最終21d、不変。Test641sourceの機械是正を当sourceへ束縛し、832TestのCheckstyle raw2705→0を確認。**製品PT0、coverage未実行、元WBS新受入0**、正式1964/53・17/190・工数null・QA051final/全安全HOLDを維持。

## 正常buildと独立後条件

PG10024-test-hygiene-six-compile-v1/manifest.json SHA5888cf524ecdc64fcb510d01ea800c6018222f1db790ad057466dae4b89072bf、当source normal六module compile/package actual0、NullAway/Werror、-DskipTests=trueのため全製品PT未実行。source/POM/資源/依存hash/実command/時刻/終了はmanifest。直前PG9992/sourcebbaとは別snapshot、旧PT成功/execを再利用して新sourceの実行成功としない。

PG10026-test-hygiene-normal-post-v1/manifest.json SHA6094f2b3027cdb314f951668c2656fbcb9b2f34c2f59a2dd9779fc146fc701c2、実0。新normal全入力は候補/反映10016/18/22のhashと一致、差分は641Testだけで、全Main1843 classは旧normalと**raw byte完全一致**。Java1800/Main965/Test835、Graph9三source原byte不変。候補CS規則/Jarと当Test sourceのhash対応も束縛し、同じ成功CSを確認目的で再実行しない。

全Test physical1922 classは同じkey集合。raw byte不変489、debug情報だけの差1433、非debug差0。新TestClassDebugOnlyMeasureはASM9.10.1のClassReader/ClassWriter(0)/SKIP_DEBUGでclassをdataとして読み、instruction/frame/handler/field/method/annotation等を保持した比較とSourceFile identityを行う。target classのload/初期化、計算対象methodの実行なし。前後全832Compiler binding/AST宣言・literal値同一との両方で機械変更を確認した。標準debug差は消して保存したのでなく、raw old/new SHAとDEBUG_ONLY判定をtest-class-structure.tsvへ保存する。execのCRCやcoverageをこの正規化で置換・合成しない。

同工具の独立合成metadata五vectorは、line番号だけの差は同じ正規化、instruction値/method名/field定数/class flagの各差は不同になることを確認。これは工具検査であり五製品PTではない。原byte/Maven class/全Main不変・AST source値保持を伴わない任意の変更へ一般化しない。比較TSV hash/全helper/ASM/実command・有限子終了/環境は10026 manifest。

## 障害・横展開と保全

BUG1787/YKT1538は固定CSの2149star/556同時宣言を832scopeで是正、641変更/191無変更。元2705/raw145は10012へ保持。556group/1553var順保持、for-loop initializer一groupは自動不適で原syntaxを維持し、CS違反対象でないことを当実0で確認。Graph9三fileは動的HOLDに伴う原source保全のため対象外であり、全835Test/全F03が0とは宣言しない。

BUG1788/YKT1539の元10014親Python1/三Java成功receiptは保全し、新10016は成功三段階を再演せず回収、残4before/6afterと候補工程を完走。12一意progress receipt/command・出力hash/全意味束縛0を10016/18で確認。現scope再試験・保存commit待ち、旧失敗の成功化/guard緩和0。

current style source5012はpush済み。10012～26の工具/公開証跡と本結果は次保存単位へ、当641Test hashのWBS traceはまだ旧bba/1798-1800測定のままなので新sourceへ推測しない。原941/943/担当費・旧source/run/予算/受入/UNKNOWN二fileを保持して次batchで結合する。全自己job39792/73671・候補stageは真正終端、外部所有UNOBSERVED_HOLD/新外部操作0。鍵closewitness二工具は未追跡未読取未実行未push、原本/鍵/Backup/stash等は不変更。

## 環境・計測・残件

既JDK25.0.4+7/Maven3.9.12/GJF1.36.1/CS14.3.0/ASM9.10.1、host Linux amd64 7.0.0-38-generic（直前host runtime実測、当normal/helperの実JDK/tool hashはmanifest）。tool追加install/モデル・推論変更/外部接続0。開始24→fresh24 used/reset1793513544、共有丸め0は専有費0でなく、N/T・配賦/工数null。usage6d00a69c、元/改訂残/開始.5-2-6cap10は不変更。

具体的増分は832Test scopeのCS指摘2705件解消と641sourceの意味保持是正であり、PT PASS件数・新機能・leaf完成件数へ換算しない。Main PMD/Graph9/実環境/native/CHR/全coverage/451・正式source/runは別未完。次は保存push/当source trace、その後未解決の静的適用性等、独立に許可されたPG/PTを継続する。
