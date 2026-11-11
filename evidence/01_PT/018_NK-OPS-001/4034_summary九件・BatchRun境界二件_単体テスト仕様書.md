# summary九件・BatchRun境界二件 単体テスト仕様書

Program NK-BAT-001 / WBS-P004-02（summary通常port）・共有依存BatchRunの正本費用owner WBS-P017-02。関連 OPS-009、UI251、SS332、SS341§3/7。Main変更なし、実DB・鍵・native・VM・Root・held四へ接続しない独立通常PT。

旧9件のInspectionSummaryPortTest sourceはPG26348の実行入力と完全同byteを維持。provider16箇所×追加IAE/NPE32入力、DTO null二入力とliteral値、有限worker停止を含む。旧8件のassert/期待値はPG26340で逆変換一致済み。実行sourceはcommit固定後のbeginへ保存する。

|Test ID|class/method|事前条件・入力|独立期待値・根拠|
|---|---|---|---|
|PT-BAT-RUN-BND001|BatchRunBoundaryTest.literalTimestampExtremesAndRedactedDisplayAreAccepted|UUID(0,1)、UTC0001-01-01 00:00:00と9999-12-31 23:59:59.999999|SS341有限microsecond時刻境界。id/cutoffは入力literalと一致、文字列は固定`BatchRun[identity/cutoff=<redacted>]`。SUTからexpectedを生成しない|
|PT-BAT-RUN-BND002|BatchRunBoundaryTest.nullOutsideRangeAndSubMicrosecondInputsAreRejected|ID/nullcutoff各欠落、最小の1microsecond前・上限の1microsecond後・123456001ns|欠落はconstructor null契約NPE、三時刻はIAE。入力の数値literalから独立に定める。NPEを業務正常扱いする実装ではない|

旧summary9＋新helper2を二class指定の単一source/単一JaCoCo sessionで実行する。元9のexecを足さず、依存6 classを一切省略せず集計する。時刻境界/null/toString追加により前回残2行1method3分岐を確認し、line/method/class/branch全100%が必要。自然branch0はN/A。失敗・abort・skipは合格へ算入しない。

事前PG26354は元群.2/.5/1ppを保持し、追加.05/.15/.3pp、改訂.25/.65/1.3pp・cap2を凍結。費用owner重複課金なし。共有枠と専用実費を分離し専用実費null。旧9の成功は保持するが全6 coverage未受入と明記する。

再現: `PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/1205_summary_eleven_qualifier.py compile`、`static`、`python3 -B .../1206_summary_eleven_preflight.py`、source固定後`1205... run <source>`、`1207_summary_eleven_post.py <source> <preflight-sha>`。出力名は一回用のため再実行で上書きしない。Java25.0.4/JUnit1.13.4/JaCoCo0.8.15/PMD7.28/Checkstyle14.3。OS・command・code・hashは実行manifest参照。

BUG2653/YKT2333の有限ownerを含む当限定経路のみ再試験し、global YKT2177、F02/F03、実DB、全PGPT正式1964/53、元190新受入へ転用しない。実行結果は4035とPG26366へ追記する。
