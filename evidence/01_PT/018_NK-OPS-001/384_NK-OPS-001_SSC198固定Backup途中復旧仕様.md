# SSC198 固定Backup途中復旧仕様

Program NK-OPS-001、隔離Root operator工具 BackupInterruptedStartRecovery/Pg480（Productionへpackageしない）。RD OPS009/UI251/SS341343353 SSC198、BUG771/YKT551/QA047旧Pairとは別。固定same boot・当回run49437eda-1681-43a9-883a-424eb55a6166/cutoff06:28:43.734078Z/親INV795eec6b633244148b40b26d0251a8ed/fresh Backup INVe5a9480ba99847779d30d3c4a321284d。可変caller name/Unit/pathを受けない。

| Test ID | 目的/事前条件/入力 | 独立期待値 |
|---|---|---|
| BREC198001 | synthetic Root metadata＋実保持FD・ゼロbyte固定marker/別public request | typed退役→marker不存在、request全literal byte不変、借用rootをcloseしない |
| BREC198002 | OBSERVING/BEFORE_RETIRE/RETIRED proof IO拒否 | 非成功・元例外同一、必要時ゼロmarker再隔離、旧request不変 |
| BREC198003 | IO/unchecked/fatal・RETIRED後故障 | 正常結果0、REISOLATING→QUARANTINED、元failure同一 |
| BREC198004 | primary＋再隔離失敗、同一Throwable含む | secondary分離/self suppression0、成功補完0、caller M/A保持必須 |
| BREC198005 | nonempty/symlink/missing/0640固定marker | mutation前拒否、別request不変、未知を成功へしない |
| BREC198006 | unlink/sync/再隔離sync fault | 退役非成功、再隔離成功又は未確定を分離、request保全 |
| BREC198007 | 全null境界/public factoryと内部source | 明示契約拒否・mutation0、NPE catch正常扱い0 |
| BREC198008 | quarantine初回/同有効marker再確認 | ゼロbyte・既inode再確認/置換0、正常同期/保持検査必須 |
| BREC198009 | 現VM全10Ref/新M-A-advisory/署名/完全pending/24table・旧411/Backup/part/request/current | 所定全実後条件・旧timeout/close未知保持、operator DB/request変更0 |
| BREC198010 | 別pending code-only→通常同run resume | 専用exact範囲だけ。old request/part保全、ABANDONEDと新beginsは通常resume内、fresh両Backup完成/Inspector/親全体/新nativeが別必須 |

Expected marker/requestは手書きpublic literal、mode/owner/type/link/phase/順序はSS198から独立指定。fakesはhostUIDをRootへ合成する限定fixtureと明示し、実VMを代用しない。IO/close/fatal/null/foreign/owner競合/再隔離不明を成功へ加算しない。仕様380の元cutoff削除oracle/旧全保全を継承、Current baseline/業務期待値を変えない。

Host command `bash tools/quality/vm/050_s1/pg480_marker_compile_v1.sh`（new v2）。JDK25.0.4/javac-Xlint:all-Werror、同bab frozen六module＋JUnit5.13.4のfixture、工具source/hashは保存commit後記。Production PT加算0・工具assertions別管理。native BREC009/010は未実行、必要coverage/451正式品質を工具成功で代替しない。
