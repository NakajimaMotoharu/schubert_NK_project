# 検査サマリーの単独非fatal SQLとraw測定

NK-DAT-001、P004-02/2、P004-05/2共有。SS331 §3.13、SS332 SSC063、SS311 SSC461、BUG-3416／YKT-2359。INSPPORT012。合成した単独のSQLExceptionでcauseとsuppressed、nextの間に同一要素が再登場する。構成したグラフにErrorは含めない。既borrowed JDBC fixtureのcomplete取得一箇所だけで返す。

期待は固定BatchRepositoryException、causeなし、suppressed 0、元のcause/next/suppressedを変えない。取得されたrow→statementを各1回閉じ、借用Connectionの変更0。有限な外側JVMで実行し、時間切れは合格に算入しない。

新1・必要既12を一execで実行する。変更されたInspectionSummaryRepositoryの実物理を固定し、JaCoCo既定と無フィルターのline/method/class/branch、CRCおよび補助型の未測定内容を分ける。実DB・全451・原項目正式受入は継続。
