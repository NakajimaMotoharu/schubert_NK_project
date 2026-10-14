# ResultCode独立oracle是正・反例仕様（BUG1244/YKT1010）

NK-PRO-001/HeaderModelTest.enumsMapOnlyApprovedWireValues/PT-PRO-001-H01・WBS-P001-01、MQ014～018/MSG001～011/UI232§7/SS322323/451。旧試験はvalues()/wireValue()からexpectedを生成し、承認外codeも往復で成功し得る。改訂oracleはUI232§7の12wire/name/profileを独立literalに固定し、集合件数・各値・decode・未知/nullと成功集合0000/0200を照合する。正常12codeはProduction不変更。

PG2630-v2は原Testを実JUnitで実行し、隔離shadow enum ORIGINAL/ADDED(9900)/WIRE(0101→0199)/PROFILE(0101 false→true)を比較。元Testは全四成功、三false-negativeを確認。shadowは新私有directoryだけ、Production file/VM/Root/DB/Backup/ADMINへのmutation0、javaagent/exec0・Production PT/coverage加点0。原版v1/session15445 actual1はlauncher版選択事前拒否（canary未実行）、payloadb69519ff/旧slot保持。v2は実fixture classpathのengineと同版launcherへ固定。

実v2/session71684 actual0/Sourcea79/TestSource68a109fbc7d6238546c426d0a416bd630b868834、04:02:24.827269Z～04:02:30.218727Z、payload33e3f41a06592df7c52b074f749f437a6a889cdc8f5023a45517b140591c1320。元source/m2/Jar hash不変・javac-Xlint-Werror0、三false-negative。公開result-code-oracle-before-manifest、private PG379/pg2630-result-oracle-canary-v1/v2。command固定PYTHONPATH pg2630_result_oracle_canary_test.py→pg2630_result_oracle_canary.py。再発防止は是正Testで同三mutation拒否＋同Main正常source全module試験・static・coverageを確認するまで未完。

YKT1010のsemantic18enum・error profile・TSV生成根拠は別対象で個別照合。UI232の集合oracleの完了を全wire/全Programの完了にしない。群0690着手前0.5/1.5/4pp、主担当P001-01の0.2/0.5/1とP002-01の0.3/1/3、参照費0。PG2620凍結sourceへの是正後付け0、正式1964/53/全leaf未変更。
