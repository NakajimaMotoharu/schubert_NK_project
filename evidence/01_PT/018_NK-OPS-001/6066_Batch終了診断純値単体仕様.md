# Batch終了観測の固定診断と拒否状態

WBS-P018-10.03/2-照合、WBS-P017-07、NK-BAT-001、OPS009・DAT009、UI251、SS331・332・341・343・351。対象はCleanupTerminalRepositoryの純値Snapshot／RejectedSnapshot。正規Batchの時刻・状態・原本操作は呼ばない。

PT-BAT-REJVAL001～005は既拒否・未終端・固定観測を継承。PT-BAT-REJVAL006は七ステップを独立リテラルで作り、別run ID二つ、11成功と一警告、固定byte135/163を与える。期待は全成功終了0・警告10、所有リスト元変更から独立、返却不変、どちらも固定CleanupTerminalSnapshot[data=<redacted>]。既001の拒否診断は別型の固定CleanupRejectedSnapshot[data=<redacted>]を維持する。診断出力は試験の固定期待を採用する。

JDK25、正規Batch／Bootstrap／Storage／Protocolに束縛して6件の同一JUnit実行を予定。実DB、本物の原本・保守・許可・退役は対象外。終了状態・対象物理・静的指摘・不足四指標は別に保存。工程正式受入の代替にはしない。
