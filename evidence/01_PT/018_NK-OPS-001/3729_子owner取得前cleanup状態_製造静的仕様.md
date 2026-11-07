# 子owner取得前cleanup状態：製造・静的仕様

BUG2477/YKT2215、SS311312341343/411451。現在closeのnew ArrayList/growthが終了試行前に失敗し得るsource経路を是正する。owner newのメモリは引数評価前（[JLS25 15.9.4](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.9.4)）、instance field initializerはconstructor引数評価後・body前（[12.5](https://docs.oracle.com/javase/specs/jls/se25/html/jls-12.html#jls-12.5)）という順序を区別する。

OwnedTestProcessがProcessBuilderを受け、failure ArrayList容量8と固定UNKNOWN IOExceptionをinstance初期化で準備、constructor最後のObjects.requireNonNull(builder).startをfinal ownedChildへ直captureする。field初期化を従来のProcess引数constructorに追加するだけでは、caller startより前にならないので採用しない。

closeは既failure list参照だけを使う。source上の記録最大は、TERM/first wait/force/second wait各catchと、終端成功時三stream catch又は不明時一例外の分岐から最大6、容量8を超えない。同owner一回/同Process wait5+5/interrupt復元/元UNKNOWN/例外identity-cycle防止は維持、graph集計の新確保は資源cleanup全試行後のまま。JVM停止/OS/実OOMからの解放を保証しない。

全五caller八箇所はbuilderの.startだけをhelperへ移し、元argv/--no-fork5/期待値/return/owner・reader・executor順を保持。old source全六fileを凍結し、逆token/独立容量算出・否定で確認。新helperだけproc:none static compile/受動javapで初期化・start・fieldcapture順を確認、元native/process Test compile/run0。own parse/format/PMD-CSとcurrent helper bytecode auxで五callerを限定静的、同source旧成功の無意味再演なし。

実ProcessBuilder.start/child操作/Root/VM/DB/FS/native/OOM注入/代替fixture実行0。実PT PASS/covはnull、source/static代替のみ。上位仕様・Main・Currentbaseline変更不要、新QA不要。追加発見/製造是正の見積1/3/7pp、cap9。新unique/whole/leaf0、442/whole94/正式1964-53/工数null・全HOLD維持。
