# 2640 Protocol frame・payload 元whole二十四件 実行結果

2026-10-30 JST、dev-foundation、開発Production6b53efeec87f3ec36a840dd8e7759656cb4aee5c、HEADaab48284ff095e65fcda00356c73251999ffa32d。2639/PG-D884・群3026原開始1/5/9pp cap10を維持。原18に同PayloadCodec必要依存の既3+3を実行前追加し、元24/5suite/F/E/S0、JVM/親真正0、元再起動0/新input・Test ID0。原見積を上書きせず追加依存をevent3027へ記録。

## command・証拠

- `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14326_protocol_frame_payload_whole_twenty_four_pt.py`、session88329真正0。
- 原 `evidence/provisional/PG14326-protocol-frame-payload-whole-twenty-four-pt-v1/manifest.json` SHA256 `2f93e52f6af6eec17f7b9a6f05fdfa48ce8365f4e8e097d02e191d491e126985`。
- `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14328_protocol_frame_payload_whole_twenty_four_post.py` 真正0。
- 独立 `evidence/provisional/PG14328-protocol-frame-payload-whole-twenty-four-post-v1/manifest.json` SHA256 `8099de1c6e2169ff4102f81db07c679b924966e2e502b2dac16155ad4fdb8d3f`。

全入力/六Main/Test/SDK/三public fixtureとfresh copy/hash、元XML24一意・八metadata反例・一sessionCRC0・元環境を照合。原実測Linux/amd64/7.0.0-38-generic/JDK25.0.4+7-1-26.04-Ubuntu/JUnit1.13.4/JaCoCo0.8.15、実command/時刻/exit/hash/fixtureのsourceはmanifestへ保存。fixture/元Source/Test/期待値/Current baseline書換え0、外部actual操作0。

## 完全Sourceのcoverage
九完全Source十physical(code9＋compiler synthetic1)。対象合計LINE370/METHOD47/CLASS9/BRANCH218全miss0。
- 各四counter100：HeaderCodec、FixedWidthEncoder、FixedWidthDecoder、ProtocolValidator、ExpectedRoute、TransportMetadata、PayloadCodec。
- LMC100/branch自然0=N/A：TransportBodyType、MessageEncodingException。
- PayloadCodec閉包に含むPayloadCodec$1はACC_SYNTHETIC4128/SourceFile PayloadCodec.java/field1/clinit55byteを確認し、Analyzerの既定filter結果全counter0としてMETADATAで照合。Codeを持つためnoCodeとは呼ばず、生成enum-switch/標準filterの根拠を記録。手動除外・filter改変・人工呼出・exec合成なし。七四100 Sourceの全閉包八physicalのうち、実行counter対象七＋このsynthetic metadata一。

2639のTest aliasは新JUnit method追加ではなく元class/methodの仕様参照名。元24の一意キーは各manifest cases/XMLで保持：MessageCodecTest7・PayloadCodecTest8・PayloadGoldenVectorTest3・ScenarioRecordEncodingTest3・AuthenticationErrorProfileTest3。対応観点は2639、全byte/hex/固定hash/型/range/immutable/null/copy/共有8threadの独立期待を維持。64layoutの単純roundtripだけでなく固定golden hash64/response31、独立LGN/header/取消/4800byte recordを確認。Fixture最大入力生成のmaximumForDigits呼出はexpected hash生成と区別し、expectedは既独立TSVから変更0。合成JMS snapshot/認証error profileだけで、実broker/認証/権限/業務処理を試験したとしない。

現source限定10exec133method21suite、39Source46physical(code44/meta2)。四100二十Sourceの全閉包26physical（実行counter25＋既定filter synthetic1）、自然branch0十七Source18physical、standalone noCode一Source一physical、未達Inbound一Source一physicalを分離。metadata二physicalはnoCode interface一＋上記generated一で重複加算しない。原71WBS sideは履歴のまま、新62未結合。正式1964/53・個別17/190・工数null・QA051final/全F03-451/BUG2092/93動的HOLD・原本保全/二held工具metadata前除外維持。
