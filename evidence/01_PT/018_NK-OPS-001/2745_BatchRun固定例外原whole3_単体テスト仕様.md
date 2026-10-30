# Batch run値・固定診断 原whole3仕様

2026-10-30、着手前.5/2/4pp、主費用P017-02.01/関連P018-04.03追加0、source6b53/normal14216。NK-BAT-001/OPS-009/UI251/SS331/341/343/352。元BatchRunValueBoundaryTest全2とplatform.ExceptionValueContractTest全1、initializer/全Main body確認、変更なし。元816に含まれないことをsuite表で確認済み。

|Test ID/method|独立fixture・入力|期待値の根拠|
|---|---|---|
|PT-BAT-RUNVALUE001/cutoffBoundsNullsAndFixedRunDiagnostic|UUID(0,16)、0001最小/1582/9999最大microsecond、直前/直後/1nanosecond、各null|SS timestamp境界、許可3点のid/cutoffは入力どおり、固定redacted全文。外側3点IAE、各nullはNPE。正常化catchなし。|
|PT-BAT-RUNVALUE002/activationNullsValueAccessorsAndFixedDiagnostic|run=2026-09-12T15:00Z、固定id、各null|Tokyo民事日付は独立手計算2026-09-13、run/id同値、固定redacted全文、nullはNPE。実原本のfreshness/所有は証明しない。|
|PT-F03-EXC004/exc004StopReasonsAreNonNullBoundedAndCauseFree|各既存StopGateFailure値の例外構築、null|固定literal `application stop check failed`、reasonは同一、cause=null、nullはNPE。reason列挙の互換性全域や実停止確認には換算しない。|

対象全四Source=BatchRun/MaintenanceActivation/StopGateFailure/StopGateException（全四physical）。pure値/固定診断だけ、実Gate/Root/Unit/DB/VM/鍵/私有IO/業務再送なし。並行/再送競合を持たない値型で、外側処理は非該当かつ未受入。

command `PYTHONPATH=tools/quality python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14690_batch_run_diagnostic_three_pt.py`、元3/2suite/一fresh JVM、F/E/S/not-run0/全normal input/六Jar/原環境、post14692で一session/CRC/全closure/四counter/null/八metadata反例を独立照合。自然branch0はN/A、未達は保持、旧成功/coverage合成0。各manifestに実行日時・環境・branch・source・command・exit・XML/exec/hash/owner/実counter、結果2746。正式・工数・全HOLD不変。
