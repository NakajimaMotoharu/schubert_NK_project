# PG541 借用transaction timeout投影件数境界

Program NK-BAT-001/NK-OPS-001、MaintenanceMutationGuard.bind、RD OPS009/DAT009、UI251、SS341§7.3/343§6.17/SSC119、451487、WBS-P017-12.01。PG539群予算1.17/3.17/7.17を継続、親/他子/共有費へ重複配賦0。Main変更なし、当PG540全六成功は保存し影響storage/bootstrap/batchだけ選択全suiteで実行。

PT-MG541001：専用synthetic PostgreSQL schubert_batchでborrowed TXを開始、public JDBC projectionを0row/2rowへ変更してbind。同owner remaining10秒・query timeout上限5秒に対し、件数がexact1でないのでSQLDataException("maintenance timeout unavailable")/cause null。期待値はSQLの単一set_config射影契約と固定literalから独立作成する。emptyではnext1、duplicateではnext2、ResultSetとStatement close各1、commit/rollback/Connection close0、borrowed Connection開・autoCommit false。実SQL SHOW statement_timeoutは5s、caller rollback後autoCommit trueへ戻すとSS role既定30min。DB/model原本/VM更新0。既remaining境界/null/異値/IO/unknown/releaseは同suiteで再確認。

実command=bash tools/quality/vm/050_s1/pg541_timeout_pt_v1.sh <frozenHEAD40>。JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4.0、offline非空三module。src/tools hash・actual exit/XML/FES/static/四counterを照合、private pg541-timeout-cardinality-selected-v1.*とartifactsへ保存しsafe manifest/hashを対応。全6/native/CHR/正式をこの選択runで合格化0。Production byteはPG540 frozen jarsへ比較し、旧a2のclass差を隠さない。未実行/失敗は未達、BUGの実装済違反は修正前登録。

実行source3d080b1ab2a486cfac48411ed99d1ed5c757a79a、2026-10-08 10:01台～10:08:03JST、actual0/source不変/405秒。storage158/bootstrap257/batch1109=1524PT/211suite、全XML Fail/Error/Skipped0、NullAway compile/SpotBugs3module0。当class 0row/2rowを含む3PT成功、LINE/METHOD/CLASS/BRANCH全miss0、借用TX所有・close各1・caller rollback後30minを独立SQLで確認。全715mainclass byteはPG540 frozen3module同一。
全XML/jar/exec/staticをprivate pg541-timeout-cardinality-selected-v1-artifacts-v1へ封印、safe SHA019fabc265f7945bf03a097d54457bd9980af1319beece86de3fc43fb0ba2946。P01712実行15/宣言1のmiss715/66/1/138（前140branch→138）、486当一WBSのみsource/run/hash/PG540 baseline byteへ束縛。WBSaudit/独立管理7test PASS。正式24/1964/53scope・VM a2/native9未変更、全source/全native/CHR/global100/ITSTは未認定。新BUGなし、旧失敗原物・Currentbaseline・原本DB/Backup/stash7/Scenario3保持。
