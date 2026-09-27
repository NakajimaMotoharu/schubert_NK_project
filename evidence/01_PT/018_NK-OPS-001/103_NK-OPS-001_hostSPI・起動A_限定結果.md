# Host SPI / 起動A限定結果（PG293、未認定）

対象は833f22f9b/dev-foundation＋Storage変更、2026-09-27 18:27:20 JST。Storage clean verify141PT・failure/error/skipped0、全6counter missed0（instruction5107/branch413/line988/complexity421/method214/class29）、SpotBugs0/NullAway/Werror成功。選択24PTの成功後、module全体を検証した。

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 PATH=<同JDK>/bin:$PATH ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-storage spotless:apply clean verify`、exit0。Linux7.0.0-34/JDK25.0.4/Jacoco0.8.15/SpotBugs4.10.4.0。入力/独立期待値は102、source/test/XML hashとcoverageはprovisional PG293 manifest。

Native010: SSH隔離VM Ubuntu26.04/Java25.0.4、Production Storage target classesだけを反映したtest-only payload、固定systemd-runのProtectSystem=strict/NoNewPrivileges/ProtectHome/PrivateTmp下で `NativeHostDirectoryProbe` を実行しexit0。hostReadOnly=false/privateReadOnly=true/sameIdentity=true。raw Invocation/journal、VM/credential/DBはGit外。PID1 provenance/Aの物理入場/current permit/Production release同一性は未合格。Unit sandboxを変更していない。

XFD008は新helperでProduction A＋別sealed proofのsamePID native exec/公開20bytes/seal15/競合20→終了後0を再試験した（旧fixtureの同OFD proofとは別）。A低位成功だけで起動許可しない。既存承認済み動作の違反は発見していないためBUGなし。SSC086/087対応中、全Production security横断回帰は次の保存sourceで実行する。正式run24/1964PT/53scopeと中心48.3%は据置。
