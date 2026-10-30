# 2865 API OutboxObservationSource原whole20 単体テスト仕様

NK-OPS-001/WBS-P018-09/RD171/UI252/SS311・332・342・351/1854・1860、Production6b53/normal14216/dev-foundation固定。event3263で元2/6/10pp cap10を実行/Fixture確認前に固定。Main/原Test356行は先行次範囲調査で全読、RepositoryTestのRow/Fixture全field/initializers/bodyは行1～185で全読、DbPoolObservation Fixtureと必要Repository Mainも全読。原whole20はcurrent1677 suite/Source集合に未登録。

Test ID outboxSource001～020：001constructor null/002unknown strict mode、003STANDARDはJDBC未読、004initial/missingはempty、005Standard null boundary、006/007null入力は前snapshot不変更、008shuffled ERROR7/PENDING3/SENT5とages6/2/4の独立値、009empty結果だけ確定zero、010immutable前snapshotと新11/13、011SQLexecute failure/012prepareRuntime/013nextErrorでmissing/identity・解放、014JDK二close失敗のprimary/secondary配列、015statement Error、016明示invalidating/recovery、017query終了/PSclose前にmissing二回で再公開阻止、018二writer順序、019pureSDK text六固定seriesと追加JDBCなし、020missing NaN→確定0→missing。expectedは固定literal/独立callback/close順でProduction method生成0。asOf固定Instant.EPOCH、threadpool最大2/Future10秒/latch解放finally、親180秒。

FixtureはJava ProxyのConnection/PreparedStatement/ResultSetだけ。許可getter/prepare/timeout1/executeQuery/RS・PScloseは固定dispatch、接続のmutation/close/commit/未知操作はAssertionError。固定SQL oracleは独立Fixture定数 `SELECT status, COUNT(*) AS row_count, MIN(created_at) AS oldest_created_at FROM schubert.mq_outbox GROUP BY status` と一致をassertする。RowはOptional/OffsetDateTimeの固定値。DriverManager/DataSource取得/実DB/ファイル/SQLserver/VM/Root/鍵/配備/networkなし。java.sql.SQLExceptionの型使用はこの確認済みfakeに限り通常PT。原RepositoryTest10/PoolObservation8はcompile-only、既成功再演/加算0。

## scopeと未実行overload

全20はobserve(Connection,Instant)のみでApiReadOnlyObservationAttemptを生成・readしない。JDK getSuppressedの固定一段配列assertだけで、独自Graph分類器/循環/深掘りなし。ReadOnlyAttempt/ObservationContext/CleanupPublicationの故障wholeは別Graph HOLDのまま。Main Sourceにはobserve(ApiReadOnlyObservationAttempt)が実装されているが本wholeでは未呼出、したがって全一Source二classのmethod/line/branch coverage未達が残る見込み。実測値と未達lineをそのまま保存し、原20ケースの成功とProgram/四counter/451合格を分離する。安易な除外/未実行→100/未知→成功0、未達を閉鎖せず後続依存へ残す。

command: `env PYTHONPATH=tools/quality python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg15204_api_outbox_source_twenty_pt.py`。Java25.0.4/freshjavac -proc:none -Xlint:all -Werror/六normalJar。post15206は同一exec/CRC/全一Source二Code closureを測定、独立15208で全原20宣言XML/fixture未選択/Source未実行overload/SS351/実ownerを確認する。元OS/JDK/時刻/command/exit/source/hash/input/XML/exec/coverage/BUGを2866/public manifestへ。実測前は未確認、manual除外0/公式filter不変/execunion0、Failed-flaky-skipped-not-run合格0。障害は修正前915/916。

正式1964-53/歴史17-190/工数null/QA051final/451-F03-G07/全安全HOLD維持。ownSDKのGC handleは保持解放、forcedGC/heapdump/targetprocessなし。Fixtureのread/cleanupをactual source/lifetime/native/実DB資格に換算しない。
