# SCR003 検索フォームの現候補12件と単一coverage

WBS-P016-03/2、FUN-003、UI222／223／234、SS313、SS323。フォームとwireの固定期待はPT-WEB-214～221／PT-SCR003-WIRE-001～002。公開FieldとCodeの順序、名称、配列の独立性、未知値、nullは `WebPublicEnumContractTest` の検索対象2メソッドで確認する。

- PG43598。現フォーム8件とwire2件が成功。旧版のwire結果はFieldCodec等が変わっているため現試験へ転用していない。対象3 classのLINE90・BRANCH42全到達、METHOD25/27。未到達は公開enum二種の `valueOf`。生coverageの読取で不要な合成名を指定した初回を保存し、元JUnitは再実行せず実際の3 classだけで再読取した。
- PG43600。補助型不足でJUnitの選択解決が失敗し終了1。XMLのError10行はdiscovery失敗に由来し、テスト開始0。BUG-3717／YKT-2917として保存。
- PG43602。現と一致する既資格補助型8と明示selectorを用い、同じ3 classについてフォーム／wire 10件と公開enum辞書2件を単一execで実行。12件すべて成功、失敗・エラー・skip・未実行0。LINE90/METHOD27/CLASS3/BRANCH42すべて到達。旧streamの合算や除外は行っていない。

原コミット・JDK25・実行command・原JUnitとexec・class CRCとhash・生カウンタは [PG43598](../018_NK-OPS-001/evidence/PG43598-scr003-search-form-current-boundaries/manifest.json)、[PG43600](../018_NK-OPS-001/evidence/PG43600-scr003-discovery-before-v1/manifest.json)、[PG43602](../018_NK-OPS-001/evidence/PG43602-scr003-search-form-enum-qualified-one-exec/manifest.json)。局所実行により確定したのは検索フォームの値・電文と列挙辞書。Web全体の正規JAR、実HTTP・DOM・CHR、451と終了依存は引き続き必要。
