# NK-OPS-001 private子directory新規作成実行結果

PG186/SSC068/031・PT-OPS-CDIR-001～008。正式PT-WEB-20260920-04/source e63b7d045fa7d64aa532fa95494020e3c4492514、02:27:35～02:39:18 JST、clean verify 11:41/exit0で認定。全1471PT、failed/error/skipped0、6Java全4coverage100%、Production5静的解析未解決0、38scope/48負canary成功。新8PT/OPS1部分成果を加算し、OPS16部品134PT・全70部分成果681PTとなる。SSC068はprivate能力範囲のみ完了。

正式Storageは15class/113method/554line/177branch全missed0。正式command・環境・入力期待実際・sourceと証跡hashはevidence/manifest.json、raw log SHA256は`b01c4c44fdba5a613221f0816c21cae480e562f1d68d1e450298223305029615`。以下の選択実行は履歴であり、正式sourceは上記に固定済み。

`/tmp/pgpt-pg186-green.log`: 2026-09-20 02:26:01 JST終了、12.009秒/exit0。Storage全82PT（既存74＋新8）、failed/error/skipped0。cleanからのJaCoCoは15class/113method/554line/177branch全missed0、NullAway/Enforcer/Spotless/SpotBugs成功。default能力、Linux mkdirat0700、Owned createと所有移送lambdaの新4method/18lineを含み、既存分岐分母177を全網羅。coverage除外/新静的解析抑止なし。SHA256 `1d960ee0bdbbaba85545afae46d1bf68e5f8ac3b9939b2f3dced04766093d5eb`。

実Linux temp directoryで0700/同UID・device/空集合・inode保持、child→parent fsync順、返却childを親close後も利用可能、親borrowed/child独立closeを確認。既存directory/file/symlink不変、null/名前/closed/不正native FD/長名、全4body失敗位置×4例外型、2sync×4primary×5close＝40複合、未対応adapter mutation0、保持親path置換、8並行成功1/collision7を独立oracleで成功。partialは削除/repairせず保全、FD bookkeepingはnative open/closeと原子的に更新して数値FD再利用を誤検知しない。backup専用UID・実root配布・archive生成は本低位PTの対象外で未完了。

環境Ubuntu26.04.1/Linux7.0.0-31/amd64/glibc2.43/JDK25.0.4/Maven3.9.12、branch dev-foundation、source cc778840＋当Production/test変更。正式sourceは後続clean全reactor前に固定する。command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-storage -am clean test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`、先行spotless:apply成功。

新障害なし。031のinput/操作/独立期待と上記実際をTest IDで対応し、正式sanitized XML・source/command/OS/tool/coverage/hashは全reactor後の018/evidence/manifest.jsonへ記録する。現行baseline/上位外部期待不変更。全PGPT・IT/ST完了ではない。
