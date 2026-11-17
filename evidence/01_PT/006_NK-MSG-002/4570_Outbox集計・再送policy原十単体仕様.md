# Outbox集計・再送policyの単体仕様

WBS-P006-02/F03、451、SS324 §8.3/SS332 §7.2、PT-IDEM-010・PT-IDEM-010-RETRY-CATALOG。元OutboxPolicyTest 4、OutboxDispatchReportBoundaryTest 3、OutboxValueContractTest 3を保つ。正時刻は独立した遅延表と指定したUTCから、集計は加算範囲と手書き値、負値は未知名、null、上限超過、時間のoverflowを使う。追加のcatalogは唯一INSTANCE、返却配列の防御コピー、未知名・nullへの固定例外を検証。Main・旧期待値不変、実JMS・DB・ファイル・権限の操作なし。BUG-3219、YKT-2431、証跡PG38286以降。

試験設計の確認で、元OutboxValueContractTestが同じcatalog／配列所有を独立に検証済みと判明。追加draftを起動前に保全・除外し、元whole10をそのまま対象とする。Main/Testのコンパイル再演なし。
