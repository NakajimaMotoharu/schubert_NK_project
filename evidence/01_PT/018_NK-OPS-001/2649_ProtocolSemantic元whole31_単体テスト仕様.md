# Protocol semantic・型・ページ境界 元whole31：単体テスト仕様

2026-10-30、Production6b53/保存5f29ce1a1660002609485903712941f508559661、dev-foundation、PG-D889。群PROTOCOL_SEMANTIC_ORIGINAL_WHOLE31_V1：原開始1/5/9pp/cap10。着手前に元7Test1819行＋IndependentNamedFieldOracle392行・値/Main38と必要依存/初期化を点検。選定読取はgroup marker前も含み実費未測定null、時刻を遡及しない。

## 範囲・独立期待値・PT_DEFAULT

既存SemanticFieldValueTest4/ProtocolSemanticTypeTest5/EnumWireCompatibilityTest2/PayloadSemanticValidatorTest8/SemanticDirectBoundaryTest3/PayloadPaginationBoundaryTest3/PayloadTypeCatalogTest6=31/7。全methodは元名のまま、一意classname#methodをXML/manifestへ保存。新Test/入力0、変更sourceを作らない。関連NK-PRO-001/002、RD171/172/UI233～237/243・SS322/323/333/351/354。Main owner P00102/03・P00201/02、Testのownerは正本485で確認しUNKNOWNを補完しない。

- scalar/ID/enum：固定日時20260902123456789/Instant03:34:56.789Z、UUID literal/大文字/欠落/未知、N12 1/999999999999/0/1000000000000、int overflow、HTTP99/100/599/600、elapsed0/999999999/1000000000、Optional present/unset/null/型不一致、18enum承認name-wire literal全表。NFCとpath512/segment255/絶対/drive/親/制御文字はString値検査だけ。hash比較は同値契約であり独立numeric hashの証明ではない。
- named mapper：公開named-types-ss323.tsv、named-accessors-independent.tsv、fields-ui234-236.tsvの固定hash。独立oracleは69型295component/79optional/空4、公開constructor/getterと方向別wire値を照合。Reflectionはこの公開固定型/fieldbindingに限定、private順序・Production生成器からexpectedを作らない。Production factoryはactual input構築にのみ使用。roundtripは補助であって独立oracleの代用ではない。
- semantic/page：固定field置換によるrecord順序/inline200-201/4800byte length×count/通知状態と削除後回答/日付片側・31日/366日境界、password11/12/128/129・emoji64/65、HTTP method/path、page2/101件/first-last101、最大page999999/99999900、単field不整合。実業務/認証/取消/DBの操作ではなく純値validate。
- enum compatibility：自作固定Java enum grammar/descriptor bytesと自分のByteArrayだけ、外部からの不明deserializationは無し。

全Test/initializer/helperとMainは純値・JDK/固定DTOのみ。Main PayloadTypeCatalog/Validatorは既読全bodyかつ当hash固定、DTO依存は旧2457の純値全module点検に対応する元Main不変更を保持（旧PT成功の転用ではない）。resourceは固定公開三TSVをfresh own classpathへ同byte複製し旧fixtureを書換えない。実Filesystem解決、DB/broker/VM/Root/permit/cohort/鍵/held操作/Graph9なし。正常・境界・異常・例外/nullを元assertionで実行し、業務並行・再送は当scope非該当、業務受入へ膨らませない。

## command・環境・coverage・証拠

`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14360_protocol_semantic_whole_thirty_one_pt.py`。normal14216固定snapshot/sixJar/SDK/元sourcehashに結合しfresh元Test+oracleをcompile、一つのJUnitJVM/一exec、envは元実測を保存。元全31/FES/aborted/not-run/exit/command/OS/JDK/branch/time/input/fixture/coverageのhashはpublic PG14360へ。PG14362独立は完全Main38 Sourceのclass閉包（DTO69/FieldValueSet等非target依存のcoverageは受入へ含めない）、四counter/同CRC/session/XML/八negative/ownerを照合する。branch自然0=N/Aとmissを分離し、低coverageを安易に除外・人工到達・無意味assertで埋めない。元14326等の成功/execを合成しない。

結果2650へ。正式1964PT/53scope・17/190・工数null・全F03/451/QA051final/HOLDは不変更、BUG発見時修正前915/916。元試験を確認再演せず、通常小区切りでは継続。toolchain JDK25.0.4/Maven3.9.12/JUnit1.13.4/JaCoCo0.8.15は元manifest資格へ結合。
