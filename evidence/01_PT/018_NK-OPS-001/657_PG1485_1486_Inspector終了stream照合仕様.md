# NK-OPS-001 PG1485/1486 Inspector終了stream照合仕様

関連: SS324§12、SS331/V011、SS342/343/354、UI251、451。対象はPG1462真正Inspectorの保存nativeと当Main769 byte。工程PT、正式source/run受入ではない。

|Test ID|目的・入力・操作|独立期待値|
|---|---|---|
|PT-OPS-INS1485001|root-private保存terminal/closing各17315byteとPID1 journalをNOFOLLOW・同九fieldで読取|固定SHA、root:root600/nlink1/ACLなし、guest boot3d69とrelease BOMecae、Main769。同じ業務操作を再発行しない|
|PT-OPS-INS1485002|真正PID1 boot/invocation/job13787/13934からstart/stop時刻を取得|手書きgoldenの丸め2000/4001ms、foreign/missing/duplicate/Root元1800秒外を拒否|
|PT-OPS-INS1485003|独立Java NativeClosingSelect1411で2streamを比較|同session/start、start-stop実時間内、terminal true probeがclosingでfalseにならない。手書きsession/probe正常・境界・null・異常20assertions。session実値は非公開|
|PT-OPS-INS1485004|closingのみ当Main batch JARへCRC照合|classByteMismatch0、terminalは保存のみ。Production実装からexpectedを作らない|
|PT-OPS-INS1486001|旧資格済19input全hash＋新closing1を固定、6module counter/XML算出|計20入力、Bootstrap/Inspector terminalを混入しない。同Main CRC0、XML4counterと独立NativeCoverage結果一致。旧counterより退行しないがgain量は実測値とし事前に架空の値を固定しない|
|PT-OPS-INS1486002|manifest qualified predicateの独立handwritten正常/欠落/null/foreign/bool-zero/false変異|不明・失敗・異source・非monotonic・同session unionを拒否。Production PT件数には加算しない|

実行: `python3 -B tools/quality/pg1485_inspector_closing_qualification_test.py` → `python3 -B tools/quality/pg1485_inspector_closing_qualification.py` → `python3 -B tools/quality/pg1486_inspector_latest_counter.py` → `python3 -B tools/quality/pg1486_inspector_latest_counter_test.py`。

環境: hostUbuntu/JDK25.0.4/JaCoCo0.8.15/ASM9.10.1、guest boot3d69固定。Root1456 failed143は成功化しない。新DB/Unit/start/stop/epoch/intent変更0。再送・並行業務を本readonly工具で人工実行しない。canonical recovery/native正式全runは別未完。

結果・hash・時間・commitは658とprivate manifest、公表safe manifestに一意対応。要求coverageは451のまま、本工具成功をJava全coverage100%やIT/ST合格に置換しない。
