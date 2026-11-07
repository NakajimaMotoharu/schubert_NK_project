# Web停止signed時計境界・BUG2409/YKT2154

対象NK-WEB-002/NK-OPS-001、WebRuntimeStop.begin/close、既Step全phase。canonical owner/cost WBS-P018-06、既RD運用停止/UI314/SS314§10・SS342/352、PG-D377。上位仕様の変更なし。追加発見の是正費を原計画消化と分離する。

PT_DEFAULT: 既存WebRuntimeStopTest全体と同じ純粋なLongSupplier/AtomicLong/lambda、JDKの例外、Tomcat LifecycleException値だけ。SessionStoreException.preserveFatalは一時Throwable graph walkだけで、DB操作しない。Main-only正常JarのWebRuntimeStopを直接試験し、native/Web起動/実HTTP/JMS/DB/Root・四held型へ接続しない。閉鎖済み5件の無変更再演ではなく、変更後sourceの必要回帰として全6件を確認する。

| Test ID | 入力・操作 | 独立期待値・根拠 |
|---|---|---|
| PT-OPS-NWEB-STOP006 | clock start=9223372026854775807、第一phaseで9223372031854775807へ進め、次phaseへ。別ownerは同startの後-9223372016854775808へ進めclose | SSの相対30秒から経過5秒を引き残25秒。phase残30→25秒、正常終了。別ownerは30秒+1nsで残0、固定IOException、後続phase0回。signed longの2^64折返しを独立整数計算で手組、Productionからexpectedを生成しない |
| PT-OPS-NWEB-STOP001 | 既source全body | 正常順/30→28秒/反復close一度/constructor null拒否 |
| PT-OPS-NWEB-STOP002 | 既source全body | IOException時に後続保持、元deadlineで25秒、成功phase再close無し |
| PT-OPS-NWEB-STOP003 | 既source全body | exact deadline残0は成功、+1ns超過は後続保持し固定失敗 |
| PT-OPS-NWEB-STOP004 | 既source全body | lifecycle/runtime失敗の固定化、phase非進行・二回再試行 |
| PT-OPS-NWEB-STOP005 | 既source全body | 直接/入れ子Errorの同一性、後続保持 |

最初は元normal21922のMainで006だけを実行し、期待された既存不具合の失敗を保存する。PASSに算入しない。修正後のMainをGit固定し、所定Main-only build/六module静的/NullAwayと、当source全6件を実行する。単体commandはinput158のmode/normal/slot/sourceと各begin.command/真正stage terminalを保存する。JDK25.0.4、JUnit1.13.4、JaCoCo0.8.15、Tomcat11.0.25、原tool pinを使用。

CoverageはWebRuntimeStop.javaに属する全physical2（本体とabstract Step）をnormal Jar同byteでreportへ含める。Stepは実行code/counter無しを明示し除外しない。本体line/method/class/branch全100%、全既例外/境界、constructor nullを確認。依存SessionStoreExceptionの別source部分coverageを当sourceの全体資格へ加えず、旧execとの合算なし。全体451/native/CHR/正式1964/53、BUG2407の未実行6件は別未完。Test新規1と変更後再資格5を区別する。

実行・source/run・入力hash・exit/XML/F/E/S・CRC/session・coverage/静的・BUG・manifest hashは3627結果へ追記する。現時点未実行、工数率null。
