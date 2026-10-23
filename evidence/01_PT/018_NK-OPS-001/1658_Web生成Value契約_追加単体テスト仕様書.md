# 1658 Web生成Value契約 追加単体テスト仕様書

NK-OPS-001/P01809/C07/RD171-MON005～013/UI252/SS313351/451§4、BUG1663/YKT1413/group1881。HttpMetricContract.Labels一record・Metric/Route/Method/Status四enumの生成14method（equals/hash/text/accessor3＋factory8）が対象。元source19cの23PT/四100を保持、生成oracle不足だけをTest-onlyで補う。public source/constructor/clinitはJDK enum/immutable map/list定義だけ、既Valve fixtureは自己所有memで実HTTP/server/DB/network/Root0。

| Test ID | 対象 | 入力・操作・独立期待値 |
|---|---|---|
| GENWEB001 | Metric/Method | 固定literal→typed constant対2/10、全値factory・未知/null拒否・values返却配列変更後の新配列不変 |
| GENWEB002 | Route | 固定35literal→typed constant対、全factory・未知/null拒否・配列copy、既routeテンプレートvectorと分離 |
| GENWEB003 | Status | 固定5literal→typed constant対、全factory・未知/null/copy |
| GENWEB004 | Labels | LOGIN/POST/SUCCESS、自身/同値別instance/null/他型/各field一差・全accessor、JDK Enum final identity hashの31-fold独立計算・固定全fieldtext |

expectedをvalues/valueOf/Labels hash/equals/textで作らない。generatorはjavac25.0.4/JDK ObjectMethods、既公式JaCoCo0.8.15 filterのplumbingを直接通常契約で補い、14をcoverage分子/分母へ加算しない。全手書きconstructor/validation/logicは実9＋metadata一・除外追加0。必要既23＋新4を当source27PT4suiteで実行、正常六Main/Test compile/Jar全1738byte/source・SDK/CRC/session/四100/static全raw理由へ結合する。元4222/common44/成功確認だけの再演0、別sourceAPI/Batchのcounter合算0。

原runPG7434、独立post7436、六compile7440、byte/trace/review7442以降予定。環境・実行command/日時/branch/source/exit/XML/input/output/hashは原manifestと1659へ保存。Failed/flaky/skipped/notrunはPASS0、null契約negativeは生成JDK enum factoryの明示拒否でProductionのNPE正常化ではない。開始見積2/4/8pp上限10、追加発見を元計画消化へ加算0。正式1964/53・原190新受入0/工数null/QA051final/PTALT0/whole451/native/CHR/actualHOLD不変更。
