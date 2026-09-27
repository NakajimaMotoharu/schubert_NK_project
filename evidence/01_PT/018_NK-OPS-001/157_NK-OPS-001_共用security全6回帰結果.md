# 157 共用security横断全6回帰

451/471 D02/04/05/R1、SSC095096、PG313。POM Gson compile＋固定署名/BOM/securityの横断変更trigger、target source `f8d8dedc3d7cb660499bb7eae2ecbef8e4312f0a`、branch dev-foundation。source/test/config/tools固定でclean test/report/staticを実行し、2026-09-28 04:28:14 JST exit0/BUILD SUCCESS。Protocol80/Storage149/Bootstrap167/API742/Web555/Batch508＝2201 PT、failed/error/skipped0、全6 SpotBugs0。

`evidence/provisional/PG313-regression-2201/manifest.json` にcommand/OS/JDK/Maven/Node、moduleごとの全327 JUnit＋6coverage＋6static（計339 file）hash、全1044 compiled class hash、未網羅class/counter、rawloghashを保存した。次test/source変更前に全採取完了。source/runを旧PG312別sourceと合成しない。

Protocol/Storageは全counter missed0、新Approval/Signature/Profile全6 concrete classもmissed0。次は未除外・未合格のnative/main counter実測:

+- bootstrap: BRANCH missed0/covered704, LINE missed7/covered1358, METHOD missed3/covered259, CLASS missed0/covered42
- api: BRANCH missed1/covered2791, LINE missed19/covered7538, METHOD missed3/covered1117, CLASS missed0/covered244
- web: BRANCH missed1/covered1673, LINE missed19/covered4773, METHOD missed3/covered951, CLASS missed0/covered188
- batch: BRANCH missed0/covered3075, LINE missed24/covered5814, METHOD missed14/covered1008, CLASS missed0/covered154

旧BUG283～290の直接caseは本全回帰で成功したが、BUG271全親unknown-start終端、YKT216その他Resource、実worker/parent全接続等へ一括完了を広げない。BUG291はsource reviewで発見した未追加反例であり、本sourceには修正未反映。全release/固定署名発行/schema-before-begin/業務main/R2/実NK CHR/R3はまだ未認定。formal858713c/run24/1964/53scope/48.3%据置、native gap除外もIT/ST完了宣言も行わない。
