# 1561 ContinuousConditionWindow 単体テスト仕様書

2026-10-23、P018-09/C07共有費0、PG-D523。着手0.5/1.5/3pp・上限10pp、共有9/残91/reset1793306748・元開始0。同SS351§7継続期間は既AlertThresholdsが外部Durationを受け取る。内部依存として、入力観測列の継続期間計算を非I/Oの値primitiveへ分離する。RD MON005～013/UI252/SS351§7・10。業務/上位設計変更0。

APIはobserve(State,Duration elapsed,boolean consecutive)。State=VIOLATING/NORMAL/UNKNOWN。null、負elapsed、既時点より逆行は拒否し状態を変えない。同時刻は許容。VIOLATING初回/断絶後は0、consecutive=trueで前回から連続と明示されたVIOLATINGのみ最初のelapsedから差分を返す。NORMALは0へreset、UNKNOWNはOptional.emptyへresetし正常と区別する。consecutive=falseなら同じVIOLATINGでも新期間の0から始める。NORMAL/UNKNOWN後のtrueは前の違反期間を復活させない。

このAPIは実clock/collector/観測の真正性・実時間連続を認証しない。呼出しがない時間を自ら正常/違反へ推測せず、欠測/切断を所有collectorがUNKNOWN又はconsecutive=falseで伝える契約。周期/最大gap/再試行の新仕様を導入しない。Boolean連続宣言だけを実条件の証拠にせず、runtime接続/全C07受入は別のまま。監視対象を操作せず、例外に入力値/任意textを含めない。private data lock内は短い計算のみ、時計/I/O/callbackを呼ばない。

|Test ID / method|独立期待値|
|---|---|
|PT-OPS-MONWINDOW001 / monWindow001|初回違反0→299.999999999秒→300秒のliteral Duration、同時刻更新は差0 |
|002 / monWindow002|正常のresetと再違反0、正常の前history不復活 |
|003 / monWindow003|UNKNOWNはemptyで正常0と異なる、UNKNOWN後の違反0 |
|004 / monWindow004|明示gapで違反期間reset、normal/unknown gapの同じ境界 |
|005 / monWindow005|null state/elapsed・負・逆行の固定拒否と状態不変、次の正しい差分 |
|006 / monWindow006|Duration最大値の初回0→同値0、差分overflowしない最大正期間、1ns・分境界 |
|007 / monWindow007|自己所有executorの同一時点並行更新でも単一起点・完全終端、実sleepなし |
|008 / monWindow008|SS351 filesystem5分/critical1分の二独立window→既Thresholdの直前/到達literal severity。正常を回復期間へ転用せず、UNKNOWNでは評価しない |

Productionをexpected生成に使わず、固定elapsed差/Duration literal/severity enumを独立oracleにする。新8＋必要同package54=62PTを一固定sourceから通常実行し、全Mainの実CRC/単一session/四counter100/静的結果を独立確認する。原4222/common44の確認再演0、source/exec/counter union0。nullness/全条件・例外branchを実行、unknownを正常へcatchしない。実command/環境/branch/source/exit/XML/counter/hashは1562以降のmanifestへ保存する。
