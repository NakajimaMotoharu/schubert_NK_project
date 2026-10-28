# 2434 業務・配送・保守八Test固定literal137件・製造静的確認結果

2433/PG-D784、source db33c6a371d3dbc8e84f70462e0e56351bbb18b4（八Test private String137だけ・Main不変更/未配備）。原指摘137を是正、別に追加静的観測2件を記録しnet135減と区別した。新TestID/新physical0、Product PT0・動的DB/file/Graph9 whole NOT_EXECUTED_HOLD・coverage NOT_MEASURED、PT免除/実業務合格ではない。

|工程/元session|公開manifest（evidence/provisional/配下）|SHA256・真正結果|
|---|---|---|
|修正前八原本20378|PG13238-business-delivery-literal-v1|c6cbe7aec8329e8e6e21b397cd65ebc6fd863bf013b59cc4b7c2abd8c8f1f385 /0|
|原preflight67729|PG13240当slot|guard1、137是正以外に新2検知・全input/observed/元PMD4-CS0保存|
|必要な原Login静的比較20755|PG13241-login-original-static-delta-v1|706fe062f667570d28fdd0b62844ac76cedab545c83864029c8988288e9f66fd /0・原にも同二件|
|元出力回収22269|PG13239-business-delivery-preflight-recovery-v1|4a09dd839415e6b4728e8913f3e4ecfc5da7340f861ee5fe297f868f9432c4fa /0・主PMD再演0|
|原基準補足64535|PG13243-business-delivery-baseline-refinement-v1|d31e0979ee6ca7808e165673b763ee16d2e401faef05bd31b5ac22fc2463960f /0・8反例・code/PT0|
|当source六normal40946|PG13242-business-delivery-literal-v1|73d770b42807892d7b39bdc6d7da6d45e73857c152cb6aace83c0387e3239496 /0・PT0|
|fresh六static84266|PG13244-business-delivery-literal-v1|869ff7f17883cf351b5d592574fa7ac5cd1c974f9d59ee4d585fb10c68e4ba5b /0|
|独立全物理/137定数44217第一entry|PG13246-business-delivery-literal-v1|afa841e05d261034c489b8086937515390f48348022d2f8c9c133549cecd5b04 /0|
|独立binary/静的同第二entry|PG13247-business-delivery-literal-v1|e902b285cdb46dba155084e9c94311575b2f6734f1e8dbf855704ee41bb5ff6b /0・typed8反例|
|995中八SHA/32126第一entry|PG13248-business-delivery-literal-v1|d7cf2af90910d98c46c0c0727c6b95e2e4b0baa2f53dcec3bc3552b2d0a8bd8a /0|
|WBS独立同第二entry|PG13249-business-delivery-literal-v1|8893bb8a0c441ca679476ae8222bc144a600d0e766ad771161b89a867a536136 /0・8反例|

## 原137是正と追加2を分離

原八Test静的270rawから137だけを除去する期待に対し、LoginInboxServiceTestのjdbcOwnerCommitsOnlyCompleteBusinessResults/permanentProtocolNeedsConfirmedRollbackAndCloseのconnectionに新たなCloseResource二件が現れたため13240はfail-closedで停止した。BUG2043/YKT1791を修正前起票し、同じ固定解析条件の原Login全文だけを別owned slotで静的比較したところ同二件を確認。今回の文字列整理による差ではない。原全体診断での欠落理由は未確定であり、解析条件差の追加観測として残す。実DB/JMS/対象JVM/拒否PTを実行した再現ではない。

Main JdbcSyncRequestProcessorはDataSource.getConnection後のConnectionをTWRで保持、Testはcallbackで同connectionを渡して後でisClosed/commit/rollback/close回数をassertする。これはsource目的の確認であって、引渡し前の予期しない失敗・実close/例外graphの正常性は未証明。二指摘をfalse-positive/実障害のいずれにも断定せず、actualViolationnull・動的/引渡し前HOLD・実行免除falseを保持した。コード/業務/PT oracleを変更したり二件を抑制したりしていない。

原source1762の診断catalog補足は新ID PMD-NEW-PG13240-001/002として別13243へ保存。元995row/全owner-cost/旧runtime/currentQualification・原群開始raw8143/Test6641/corr1282は不変更保全し、補足時code0・原corrected0・新受入0を明示した。補足後の参照catalog8145/Test6643/refs3273/pending1120から当137是正を差し引き、当sourceの追跡catalog8008=Main1502+Test6506/corr1419/refs3273pending1183/参照なし4735へ結合。これは原指摘の追跡と追加観測の計算であり、未実施のfresh全source PMD件数や実障害件数ではない。元全体catalog/Currentbaselineを書換えない。

## 当sourceのPG/静的確認

元全文token逆と全137値＋各file assertion binding/annotation/終端161非同値反例、原133raw保持＋追加2＝135raw/PMD4・rawgate1/Checkstyle0を確認。原値/全assert/順序/所有/全Test methodは不変更。全1843Main同byte、既1974Test keyset不変・八SourceFileの44class内39だけ変化/他1935同byte/new0。正確なprivate137 ConstantValue以外の全private/public metadata・全method形状が不変。rawCode表現はCP/debugを含むため意味差の単独証明にしない。

fresh SpotBugs4.10.4/Max/Low・新sourceの六JARと固定外部aux、API467/batch645/bootstrap117/protocol176/storage80/Web358＝1843のClassStats集合と物理class集合が一致、bug/missing/error各0。独立binary内部identity/全hash・typed8反例も通過。既tool runtime byteだけを再利用し、旧Product解析/PT/coverageを新sourceへ転用しない。全WBS audit1/HOLD、995registryの八SHAだけ変更/他987row・全元担当費/旧runtime/unknown二・原941/943/見積を保持。

BUG2042/YKT1790は全137のPG/静的確認済だが動的再試験HOLDで全面完了日なし。BUG2043/YKT1791は基準追加/source目的の確認済、原欠落理由と動的・引渡し前後条件は未解明HOLDで未完。正式1964PT/53scope・歴史17/190・新leaf0・工数null/QA051final、全F03/451未受入を維持する。

群2800開始・2801で実装前fresh8/残92を追記、原2/5/9pp/cap10不変更。群開始共有7→8（同reset1793774153、他chat込み）、専有費/N/Tnull。原計画137是正、追加静的観測2、正しく停止した基準delta guard1・必要な原source静的比較1、工具不具合0/追加source再資格cycle0を区別。usage cursor2b0ccc9e（21:32:43JST/新explicit0）、次点検used10・残10以下/不明停止。保存push後はcurrent全source静的件数を一度計測してcatalogとの差を確認する。単なる同じ成功の再確認や動的HOLDの迂回は行わず、通常区切りで停止しない。
