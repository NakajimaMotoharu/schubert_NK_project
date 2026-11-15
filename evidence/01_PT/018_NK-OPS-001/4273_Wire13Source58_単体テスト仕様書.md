# Wire 13Source・58件・実Code補完の単体仕様

主WBS-F03/YKT2431、共通JMS owner P005-02、参照P016-07/10/13/14。RD MQ/AUT/FUN003～008、UI232/234/235、SS311/321/322/323/352。新Production挙動の不足はなく、既13Javaの実装・原goldenを変更せず、未実行Codeを確認するPT sourceを製造する。

PG33728は元40件の同execを再実行なしで測定し、Webの実73method中5・全82branch中18の未網羅を実証。4 facade32件は元40の一部で未試験としない。古い既定値では見えなかった二enum.valueOfのうちJMS側は既Client10が検証し、保護読取側の閉集合が新1件の対象となる。既whole57は新成果ではなく、新定義と同source/runを満たすために必要なまとめ再資格としてのみ計上する。

|Test ID / whole source|件数|fixtureと独立期待値|
|---|---:|---|
|PT-JMS-WIRE-REASON001 / ProtectedReadReasonContractTest.wireReason001ClosedSymbolsAreExactAndEnumerationIsDefensive|新1|既wire異常契約の入力不正・応答不正・一時不可の固定symbolを手書き3組に対応。valuesの順序・全3件、valueOfの同一enum identity、返却array変更後も次の列挙不変。空/小文字/前空白/未知はIAE。生成Java enumのnonnull引数契約へのnullは明示NPE拒否であり、ProductionでNPEをcatchして正常扱いしない。|
|AnimationWireClientTest / WEB238..245|既8|原SS request-byte/response/error/null/64並行・caller所有・消去、全本文/golden保持。原3871の有限pool/futureと同一source。|
|MusicWireClientTest / WEB254..261|既8|原SS request-byte/profile/bounds/error/64並行・所有・消去、全本文/golden保持。|
|ScenarioWireClientTest / WEB166..173|既8|元六request/独立header・NFC・byte/response/100並行・固定redaction、whole本文保持。|
|LogSearchWireClientTest / WEB270..277|既8|元Log request/日時/response/error/bounds/64並行・消去、whole本文保持。|
|ProtectedReadFatalContractTest|既8|元provider cause/suppressed/SQLnext/JMSlinked・有限identity graphの独立原8。|
|JmsRequestReplyClientTest|既10|原4043＋既修正の最大1/12/20・21拒否、先登録/一送信、2秒境界/1ns/割込復元、送信故障・非SQL三型・ID衝突/clock overflowの独立call-count/返却byte/permit回復。|
|ReplyCorrelationRegistryTest|既7|原2635＋六terminal順序の最初のliteral結果、100同時一勝、返却view cancel/completeで元promise不変、null/容量/期限/defensive-copy。|

期待値をProduction methodから生成しない。新symbol期待は固定文字列/enum定数、既wireはSSからの独立手書きbyteと元2635/2969/2970/3871/4043/元40原8を保持する。新1はcoverageだけの無意味な呼出しではなく、閉集合・正負入力・防御的列挙をAPI契約として検証する。生成enum/nullはJava自身のnonnull拒否仕様であり、利用者入力をNPE正常扱いする処理を追加しない。

現13MainとProtocolを含む元186 input SHAは全一致。旧NullAway/Main compile/staticの正規成果をexact byteで再利用し、未受入Bootstrap POM/CopyPortへ資格を転用しない。新whole8Testのみ現在sourceをcompile/Xlint/Werror、source整形・Checkstyle・PMDは新Test、旧7本文不変と現traceを固定する。class名194をguardしてから既許可byteをコピーし、SDKは元JMS interface/Protocol/JSpecify/JUnitだけ、実provider/JDBC/backend/Root/Actual4/Root2/native/VM/原本/鍵アクセスをしない。

新単一exec58のdefaultと実unfilteredを両保存し、13Javaの全18physical（Code16、interface/annotation自然Code0二つ）を無除外で測定する。own実Code73method/82branchを全網羅するのがこの限定目標。Protocolを含む全194 classも同execで全測定し未達を隠さず、依存を除外して全194/全Program/451の100%と偽らない。facade自然branch0はN-A、全体の実branchへ人工条件を加えない。

compiler/JDK25.0.4/Maven-root設定・JMS3.1.0/JUnit5.13.4/JaCoCo0.8.15は元40と同じ固定環境。source固定commit・各command/UTC/OS/終了code・XML各case・全input/CRC/hash/init/coverage・BUG/YKTはPG33730準備→33732preflight→33734単exec→33736独立postと補完rawへ保存する。未実行や一部成功は完了扱いしない。上限.8/2.4/7.2pp cap8、原価格/元190/正式1964/53/工数nullを保持。実根拠なしの受入増加なし。
