# 固定caseスキーマの追加制約を拒否する単体仕様

PT-CHR-DEF-SCHEMA002、BUG-3809／YKT-2967、WBS-P020-01.03/2。対象は `GateContractValidator.validateDefinitions` が呼ぶ固定case定義の検査。RD TST-001/TST-004、UI264、SS355 §5・§11 CHR-G01。

既存の六定義JSONをテスト資源から読み、合成copyを使う。元のschemaはversion 1、case配列24個、itemの必須4欄からなる。正常資料は診断0を期待する。以下は毎回独立に一項目だけ追加し、指定された診断だけを期待する。期待値は承認済みの固定資源の形とJSONの論理から定める。

| 場所 | 追加する制約 | 期待する診断 |
| --- | --- | --- |
| root | maxProperties=1。必須二項目と両立しない | SCHEMA_EXTRA_KEYWORD:root |
| properties | 固定二欄に未登録の定義を加える | SCHEMA_EXTRA_KEYWORD:properties |
| version | minimum=2。const=1と両立しない | SCHEMA_EXTRA_KEYWORD:version |
| cases | enum=[[]]。24件固定と両立しない | SCHEMA_EXTRA_KEYWORD:cases |
| cases/items | maxProperties=3。必須四項目と両立しない | SCHEMA_EXTRA_KEYWORD:item |

入力を修正せず、診断は固定文字列で返す。JDK 25、既存の合成定義JUnitを局所選択する。修正前の反例と修正後の結果・実行条件・原四指標は別の実行記録を参照する。実CHR、baseline改定、正式451、担当承認は別工程条件。
