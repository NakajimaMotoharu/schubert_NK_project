# 比較器のCurrent実行区分単体仕様

WBS-P020-01.02／2、NK-CHR-001、SS355 §5／§8／§10、UI264、BUG-3482／YKT-2778。通常の合成比較fixtureは24ケース、16 DIF、入力元を明記した独立固定期待値を使用する。

| Test ID | Method | 一つだけ変える定義 | 独立期待 |
| --- | --- | --- | --- |
| PT-CHR-DEF081 | rejectsCurrentRunCaseReportedAsNkOnly | 固定したCHR-A01のCurrentを RUN から NK_ONLY | SS355のCurrent実行23件の一つ。比較を失敗とし CATALOG_CURRENT:CHR-A01 |
| PT-CHR-DEF082 | rejectsNkOnlyCaseReportedAsCurrentRun | 固定したCHR-N01のCurrentを NK_ONLY から RUN | SS355でCurrent実行対象外の唯一のcase。比較を失敗とし CATALOG_CURRENT:CHR-N01 |

修正前は二methodの失敗を記録し、修正後は比較器全体と既constructor確認を同じ手元snapshotで実行する。Current baseline・実DB・Browser・実FileStoreは使わない。正式451の試験と分離して記録する。
