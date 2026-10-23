# 1650 API監視生成value契約 追加単体テスト仕様書（BUG1660/YKT1413）

NK-OPS-001/P01809/C07/451§4、同group1874の追加発見依存。元Outbox8の開始見積1/3/6ppは不変更、元64PT/四100・srcdbbは歴史保全。新GENMET001～008の8ordinary caseを別観点として追加し、元計画8と分離。上位仕様/quality/除外設定を変更しない。

生成元は固定javac25.0.4（`--release25`）/JDK25.0.4 ObjectMethods、実測はJaCoCo0.8.15。主対象=DbPoolMetricRecorder.Counts/OutboxRowsMetricRecorder.Countsの全七accessor＋equals/hashCode/toString六（計13method）、Async.State/DbPool.State/OperationMismatch.Operation/Outbox.Statusのvalues/valueOf八（計21生成method）。全型のconstructor/enum初期化/手書きvalue/validationも当scope15 executable inventoryに残し、既ordinaryで正分母counterを確認する。annotation-only package-info一は実行codeなしのmetadataとして別記する。

| Test ID | 入力/操作 | 独立期待値/根拠 |
|---|---|---|
| GENMET001 | Pool Counts3/5/2/8・self/同値別instance/null/文字列/各componentだけ差 | equalsの同一/同値だけtrue、全四差・null・別型false、全accessor固定原値 |
| GENMET002 | Pool通常/全MAX | hash94248/0、toString固定primitive全field文字列。JDK25 hashCombiner=31h+Long.hashCode(component)、初期0から独立算出 |
| GENMET003 | Outbox3/5/2・self/同値/null/別record型/各三差 | self/同値だけtrue・他false、全accessor固定原値 |
| GENMET004 | Outbox通常/全MAX/全0 | hash3040/Integer.MIN_VALUE/0・固定全field文字列、同上独立31-fold（production methodでexpected生成0） |
| GENMET005 | Async enum全5/literal valueOf/UNKNOWN/null/返却array変更 | 全literal→固定enum、未知IAE/nullNPE、values新arrayの先頭RECEIVED不変 |
| GENMET006 | Pool enum全4/同境界 | 全literal→固定enum、lowercase未知拒否/values defensive copy |
| GENMET007 | Operation enum全8/同境界 | 全8literal→固定enum、UNKNOWN/null拒否/先頭UCRREQ01不変 |
| GENMET008 | Outbox enum全3/同境界 | 全literal→固定enum、UNKNOWN/null拒否/先頭PENDING不変 |

標準JaCoCoのRecordsFilter/EnumFilter等によるcompiler plumbingのfilterを、生成対象が無い/実行不要/到達不能と読み替えない。custom exclusion/class/method削除は一切追加しない。21methodを上記直接通常PT/独立oracleで明示し、全Main physical/CRC/session・正分母四counter・全手書きbranchを維持する。固定JDKのObjectMethods hashCombinerは`javap -p -c java.lang.runtime.ObjectMethods`の31掛け加算と生成bootstrap field列から照合する。src.zip symlink先は存在せず一次source未取得のため、同installed bytecodeを参照/保存し推測を避ける。仕様外の将来JDK実装を保証しない。

各recordのObjectMethods/各enum生成method inventoryを独立javap/JaCoCo reportで突合し、filter対象/生成元/非影響/実21契約をreviewに明記する。生成user logicを隠す除外globやframe集計は不可。既親NullAway/SpotBugsでは生成型も除外しない。新sourceはTest-only追加、Production Mainはdbbと全byte同じであることを検証するが、元64成功を新72へ算術加算せずfresh72/9suiteの真正実行・CRC/四counter/静的/normal六compile/Jar/trace/reviewへ結合する。

実行予定はPG7402/7404以降、対象source/環境/command/time/exit/期待・実値/XML/coverage/static/BUG1660-YKT1413/evidence path/hashは元manifestへ保存。新scopeはAPI18Java/実15＋metadata一・全1738physical/80source予定、生成method契約の確認前は本群受入保留。実DB/outbox dispatcher/VM/Root/鍵/native等HOLD、正式1964/53・原190新受入0/工数null/QA051final/PTALT0/全体451は不変更。
