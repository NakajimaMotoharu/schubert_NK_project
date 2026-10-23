# 1575 Micrometer実Jar・依存差分・是正閉鎖

2026-10-23、1573/1574/group1830の続報。source `ef6f9f22aaa8b16ffcfe39952bfc9a2196b0308a`。PG7122-micrometer-http-six-post-v1真正0、manifest SHA `9e62721bb5c8d54688d863cf0c5d0cdb1574f63167a638e6672662ad99b877fd`。原7120の当六Jarを照合し全1697class＝旧1669全byte不変＋歴史Batch20同byteのみ＋当Web8（実7＋metadata1）が原7118の15件実行byteに全一致、ArchUnit五rule0。旧Batch73をsourceef6の実行済み/coverageへ転用0。SDK四Jar pinは元15実行/独立static/正規compileで完全一致した。

全32source差分＝追加31＋Web POM変更1。POM変更は既managed core1.17.1のdirect compile依存を追加しただけで、当nodeを除いて全XML semantic treeが原e7と一致することを独立確認。新scope/version/exclusionや他dependency/plugin/config/DDL/既Main変更0。Counter/Timerの記録/namespace/SDK内部aux表現は1573/1574、実exporter/公開名・quantile/HTTP terminal/Root owner assemblyは引続き未受入。

BUG1650/YKT1403はSDKがAutoCloseableでないことを自己所有fixture bridgeへ反映、全九scope/派生fixture・owned close1/borrowed close0、Test compile/15通常PTで確認。BUG1651/YKT1404は固定SDK primary bytecode7114 a7e11af5とSS九境界からprimary1785/SDK aux315を区別し、name/type/tag/le値/route各九とwrong-type partialを実assertして15件/FES0へ。元7106 PT0・7110 F4を保持し、期待値の観測合わせ/新catalog追加/静的抑制/依存除外0。修正693382137/ef6f9f22a、当二BUG/YKTを閉鎖。製造Mainはb0c43d737から不変更。

公開pathは `evidence/provisional/PG7122-micrometer-http-six-post-v1/manifest.json`、原Jarは7120 slot。実entrypoint/library/helper/loaded公開toolを採取・終了時一致、target classのload/init0/追加PT再実行0。全体451/全scope同source-run/native/CHR/正式1964-53・歴史17/source別新7・原190新受入0/工数null/QA051final/PTALT0/全actualHOLD維持。次は当32差分の要求/仕様/TestID/実行/依存traceを整備し、実SDK接続を前提に安全条件が成立する後続PG/PTへ継続する。
