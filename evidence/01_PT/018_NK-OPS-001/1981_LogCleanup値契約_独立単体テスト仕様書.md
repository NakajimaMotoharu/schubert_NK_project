# LogCleanup値契約・独立単体テスト仕様書

2026-10-26。NK-BAT-001/DAT-009/OPS-009、UI251、SS331§3.9/332§11/341§7.2、WBS-P017-07.01（関連P017-12.01）。群2233、着手前0.5/2/6pp・上限10pp。原artifact担当・原見積り・v3/v4/v5は変更しない。

## 対象・独立性

Mainは `batch.repository.CleanupReason/CleanupChunk/LogCleanupProgress` と `batch.cleanup.LogCleanupSummary` の完全4source unit。依存値型BatchRun/CleanupCountsはfixtureを作るため使用するが、その全域資格を本群から推定しない。新Testは `batch.cleanup.LogCleanupValueContractTest`。既存LogCleanupServiceTestはBeforeAll/BeforeEachがDBを起動・更新するため選択しない。本群は別の値型契約であり、サービス/DBの試験を別経路で再試行するものではない。Graph9のMain2/Test3/9IDを参照せず、JUnit lifecycle・fixture・対象MainにDB/JMS/ファイル/VM/Unit/鍵/permit/intent/ネットワーク操作なし。

## 凍結期待値

|Test ID|method|入力・操作|独立した期待値と根拠|
|---|---|---|---|
|PT-BAT-CLEANVALUE003|summaryUsesFixedDeltasAndCumulativeWarning|before=(3,1,2)、after=(10,5,5)/完了true。before=(10,5,5)と同じafter。全zero。Long最大境界。|差分は手計算(7,4,3)、再開差分(0,0,0)でも累積skipped=5なのでWARNING10。zeroは0。固定診断全文に件数と終了値のみ。SS341の累積・再開・WARNING契約、長整数の非負差分。expected生成に本番attemptCounts/exitCode/toStringを使わない。|
|PT-BAT-CLEANVALUE004|summaryRejectsEachInvalidComponent|run/before/afterの各null、別run、未完了、target/deleted/skippedの各減少を一条件ずつ独立入力。|nullは境界契約に従うNPE、他5条件はIAE。catchして正常化しない。後続条件に達するよう先行条件を正常に保つ。実commit/END/owned releaseの完了証明にはしない。|
|PT-BAT-CLEANVALUE005|progressRetainsValuesAndRejectsNulls|run/counts、complete false/true、各null。|getterは明示fixtureと同値、completeは入力どおり。nullはNPE。borrowed TXの観測であり、単なるcomplete=trueをDB証明へ昇格しない。|
|PT-BAT-CLEANVALUE006|chunkRequiresZeroCountsForEveryRejectedReason|理由の固定3値、全理由zero、OK/nonzero、拒否2理由nonzero、各null。|理由集合は固定文字列OK/LOCK_BUSY/BACKUP_GATE。拒否理由で変更件数1はIAE、全zeroは許可。返却getterと値比較。元SS332削除拒否時の変更0。|

境界・異常・nullは上記、並行・再送は不変値型なのでresource競合/再送処理を持たず、本群から外側の並行安全性を推定しない。独立Testの全methodを固定catalogで実行し、JUnitのfailed/errors/skipped/aborted/container異常0、XMLと終了codeを独立照合する。対象4source unitの全物理classを同source・同exec/session/CRCで計測しline/method/class/branchのmissed0を要求、0/0を実測100へ変換しない。未達なら具体未到達を記録し未受入とする。

source固定後に六module通常compile/format/null/lint（PT0）を行い、上記新Testだけの有限JUnit、独立coverage post、新Test PMD/Checkstyleを行う。変更前の成功を新sourceへ合算しない。実行command/source/環境/日時/終了値/XML/hash/counterは後続manifestに記録する。正式1964PT/53scope・既17/190・工数null・QA051finalと全actualHOLDは維持、本群だけで全PG/PT/IT/STを完了にしない。
