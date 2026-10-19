# semantic enum内部命名是正・互換単体テスト仕様

2026-10-20、NK-PRO-001、BUG1474/YKT1237、WBS-F03（protocol消費側は追加費0）。UI234～236/SS323/333/351/354、411/451。対象はprotocol.layout.semanticの十八enum。公開constant名・順序・wire literal・wireValue()とWireEnum契約を変更せず、private保存fieldだけwireValue→encodedValueへ変更する内部PG。RD/UI/SS外部仕様・新QA不要。

期待値の根拠：既ProtocolSemanticTypeTest.approvedEnumNamesWireValuesAndConversionMatchIndependentDesignTablesはSS/UIの明示表を独立literalとして保持。PayloadGoldenVector/PayloadSemanticValidator/SemanticFieldValue等を含む**protocol全既86件/17suite**を新sourceで再実行し、追加二件/一suiteと合わせ88/18、FES-flaky-not-run0を要求する。旧3908全体は新private renameの合格へ転用しない。

PT-PRO-F03-ENUM001（EnumWireCompatibilityTest.enum001SerializedAnswerStateMatchesIndependentProtocolVector）：正常ANSWEREDのJava enum固定streamを手書き文法から構成する。STREAM_MAGIC/VERSION=aced0005、TC_ENUM=7e、TC_CLASSDESC=72、クラス名UTF長58/独立literal完全名、UID0、flags12、field0、java.lang.Enum descriptor/UID0、定数ANSWEREDを期待とする。production serializerをexpected生成へ使わず、実ObjectOutputStreamの全byte一致と固定vectorの読戻し/末尾EOFを確認する。

PT-PRO-F03-ENUM002（同.enum002EverySemanticEnumRetainsItsFieldIndependentSerialDescriptor）：十八の型を明示し、JDK ObjectStreamClassが全型のserialized field0/UID0であることを確認。既SS tableの全値/未知/空/null・境界のnegativeと固定長codecは既protocol suiteで継続する。新rename自身は並行共有state/再送/DB/例外契約を追加せず、immutable final enumの既不変性を維持する。

実行：所定PYTHONPATHで `python3 -B tools/quality/pg5724_semantic_enum_protocol.py`。clean source archive固定、protocolだけのformat→compile/型/null/全PT/package/JaCoCo report/SpotBugs。元実XML inventory/全174物理Main、line/method/class/branchのmiss0とfailure/skip/rerun0を検査する。新source/branch/JDK25.0.4/Maven3.9.12/command/実exit/source hash/XML/coverage hashはprivate safe manifestに保存し、許可列だけ公開する。静的PMD/ABIの別点検をPT実行件数へ加算しない。

事前レビュー：三箇所だけ/各file（private宣言、this代入先、getter return）を変更しconstructor引数・public method・enum constant/literalを保持、十八以外のMain不変更を確認する。Throwable既定serialized fieldはこの変更から除外した別未是正対象であり、coverage除外やF03免除ではない。既SourcePrivateFieldRenameのSerializable拒否guardは緩和/再試行せず不変更。new-only出力で元成功/失敗を保持する。

状態：PG実装済み・独立二試験追加、実行/PMD当警告消失/ABI/新全体・nativeは未検証。実結果とhashを後記。PTALT-001の拒否範囲とは独立、代替確認として数えず通常PTとして明示する。仮想機械/DB/サービス/回収・intent/permit操作0。
