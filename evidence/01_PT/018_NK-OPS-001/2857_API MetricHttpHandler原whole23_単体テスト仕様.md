# 2857 API MetricHttpHandler原whole23 単体テスト仕様

NK-OPS-001/WBS-P018-09/RD171/UI252/SS342・351/1817、Production6b53/normal14216/dev-foundation固定。event3254で元1/4/8pp cap8を実行前固定し、先行次範囲照合でMain/原836Test行全読済みを明示。全suite/全Sourceはcurrent1631と重複なし。

原Test ID apimhttp001～023（019～023は原method長名と元XMLで一意join）：001/002ready真偽200 literal、003DEBUG7.5→9.5＋標準SDK text、004POST/HEAD/get/OPTIONS405、005末尾slash/encodedpath/info404、006query無視200、007constructor/handle null境界、008未初期化/009close後未公開、010Runtime/011Error ready失敗identity、012header IOException/013body IOException identity、014method優先405、015毎回ready変化、016stale header単値置換、017borrowed writeはcloseせずcallerがclose/018borrowed failure同様、019sample9.5→11.5とready変化、020fake pool3/5/2/8→missing NaN、021deferred supplier各一回/真ゼロ、022default API service snapshotは明示missing、023caller失敗cleanup一回。

独立oracleは固定ready prefix・200/404/405・{}・Content-Type text/plain; version=0.0.4; charset=utf-8またはapplication/json; charset=utf-8・Cache-Control no-store、UTF-8独立byte長、固定7.5/9.5/11.5・四getter順、header/body出力callback数/空出力/所有close数。expectedをProduction methodから生成しない。真readyは供給値で真正runtime readiness/200 UP受入にしない。

全fixtureはprivate memory HttpExchange/Headers/ByteArrayOutputStream/URI構文、address getterはUnsupportedOperationExceptionで実socket/server/HTTPclientなし。Api Context/SDKは自己child所有・listener保持解放、Snapshotは供給metadata、実DB/SQL/JMS/VM/Root/Graph/鍵/配備/外部接続0。原DbPoolMetricObservationTest.Fixtureはcompile-only/旧8未実行。IOExceptionは固定throw seamで実ファイルIOなし、forcedGC/heapdump/attach/targetprocessなし。WebService22/HttpMetricValveのGraphHOLDと無関係な許可済み通常PT。

command: `env PYTHONPATH=tools/quality python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg15168_api_metric_http_twenty_three_pt.py`。Java25.0.4/freshjavac -proc:none -Xlint:all -Werror/固定六normalJar/親180秒。post15170は同一exec/CRC/全一Source closure・四counter、独立15172は全原宣言XML/SS351/Code/実owner/固定HTTP契約を別読照合。元OS/JDK/時刻/command/exit/source/hash/input/XML/exec/counter/BUGを2858/public manifestへ。実測前coverage未確認、manual除外0/公式filter不変/合成exec0、Failed-flaky-skipped-not-runは合格0。障害は修正前915/916。

正式1964-53/歴史17-190/工数null/QA051final/451-F03-G07/全安全HOLD不変、実Browser/native/サーバ起動を実施したとしない。
