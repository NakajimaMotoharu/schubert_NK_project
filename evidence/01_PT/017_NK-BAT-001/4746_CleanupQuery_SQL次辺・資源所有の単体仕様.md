# CleanupQueryのSQL次辺と資源所有

NK-BAT-001、OPS-009、DAT-009、UI251、SS311 SSC-461、SS332、SS341、YKT-2359、WBS-P017-07.01。P004-05は関連参照。

**CLNQUERY010**。CleanupRepositoryのexecuteとreadLogProgressそれぞれで、文取得時または行の最初のgetterでSQLを投げる。固定SQLExceptionのnext SQLのcauseに合成LinkageErrorを一つだけ持たせる。期待はSSC-461の次辺とcauseの順序から、同じErrorが抑制なしで返ること。取得失敗ではprepare以降の呼出なし、文と行の取得0。行取得後はgetterの後に行、文を一回ずつ解放。借用Connectionへのcommit等はfixtureで拒否する。4変種。

既承認の借用JDK proxyを使う。元9件は今回の対象外。実DB、実削除、再送、並行、全sourceのcoverageは別証拠を参照する。実行環境、command、終了コード、対象sourceと入力hash、実結果はPG40866のmanifestを参照する。
