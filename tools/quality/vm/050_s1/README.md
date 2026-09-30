# 050 隔離PG/PT VMのS1実再現tool

最新PG387はsource7ba352d6f・通常resumeの実再検証282。新5toolは実使用byteを保存し、元SUCCESS/今回SKIP・fresh子・成果不変を独立採取する。PG385/386の結果を上書きせず、旧sourceのexecを合算しない。現VMはPG387なので既実行の配備・resumeを二重発行しない。

Source/試験正本はsrc、278/279、SS341/342/343。ここは隔離VM pgpt-r2-20260927-01に固定した配備・独立oracle・sanitized collectorであり、Production main/probe/StartupPermitの代替ではない。再現の実sourceはa6b5c7c8b、Release0.1.0-PG385、実正一往復278。既存結果への再書込みをしない。署名鍵/age private key/SSH key/credential/dump/raw archiveはGit外privateで入手し、Gitへコピーしない。

PG383 toolは既存22SQLと唯一のpending023を分類して専用Flywayを一度適用した履歴の再現用。現VMでは既に24履歴成功なのでmigrateを再実行しない。Pg384/385は残存INVALID原本を削除せず、同M/A・stop-all・全終端・別pin元byte署名/fullBOM・host RO・新INVALID→root400承認/current絶対selector→全BOM再読でcandidateを切り替えた。permitを発行しない。Release配置はnew-only、既存候補や退避tar/DB復旧点を上書きしない。部分配置衝突をSource gate緩和で回避しない。

配備の前提：`AssembleReleaseFixture`で固定HEAD/source-cleanを確認し全6 reactorから実thin-JAR/座標を組み立てる。Maven `-B -Dstyle.color=never`、Nodeの実PATHは`work/toolchain/node-v24.19.0/bin`。partial reactorのcached shared JAR混入はassemblerがSHA不一致で拒否するため、全6 compile/jar/runtime-copyを用いる。JAR作成成功はPT実行/coverage100%の証明ではない。OpenSSLによるdetached Ed25519署名と独立検証後、公開候補/署名/toolだけをVMへコピーする。鍵実体はVMへ送らない。

外部入口は真正 `systemctl start schubert-nk-morning-controller.service`、実Source Mainの明示resume。同Source agent bitmapsと固定metadataのみを採取する。stop後GCのInvocation空を未起動と判断せず、PID1 journalの固定UNIT/INVOCATION_ID/JOB_TYPE/JOB_RESULT/時刻だけを独立採取する。raw MESSAGE/commandline/DB payloadは収集しない。

NativeReached/NativeCoverageは標準JaCoCo0.8.15＋ASM9.10.1を使い、全分析classのisNoMatchをcovered filter前に拒否する。未一致byte/他Source結果を混ぜない。coverage unionは暫定の同byte採取で、正式53scope・全4指標100%を代替しない。full six collectorはJUnit properties/stdout/diagnosticsを落としcount/time/Test ID相関を保持する。failed Node実行は別manifestへ保全する。

`check_pg385_artifacts.py`は実tarをprivateで読み、固定run/cutoff/handle/version、全3artifactの独立hash/size、config7/credential16の正確なregular集合、独立age復号を確認する。秘密値を出力しない。dumpの復元一覧224entryはVMの実pg_restore --listで値を捨てcountだけ確認済み。collectorのfile hashはProgram manifestへ保存する。実private入力を持たずに架空の値でPASSを作らない。
# PG386追補

Pg386TrustedDeployment/pg386_deploy/pg386_place_releaseとBackupFailureFixtureは隔離VM限定の実使用tool。後者はM/A・全8Unit停止・署名/fullBOM・INVALID原本・root0600 inputを検証し、元byteをprivate force保全してから負入力へ変更する。復元済みの現VMへ再実行しない（new-only保全path）。PG386 collectors/oracleはsource d49固定の真正既知失敗と復元後成功を保存する。受入/permit/通常resume正当性の代用ではない。秘密key/input/dumpは同directoryへ置かない。BUG349の値比較修正と実試行結果は280、追加横展開negativeは継続。
