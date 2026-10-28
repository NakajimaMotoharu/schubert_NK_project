# 2488 Log検索wire PMD半開区間是正仕様

2026-10-29、BUG2071/YKT1819・PG-D810予定、event2867/開始0.5/1.5/3pp/cap10/fresh24残76。source17ab52b25/保存2396b80f3（push97505真正0/remote一致）、主F03/元P01614担当費参照内数。結果2489予定。

既13620/22の二PMD08082/83は、JavaSE JUnit threadのsource/method/実case結合は保持するが、sourceSpanSha256がPMD endcolumnの一origin/exclusiveを正しく半開区間へ直しておらず隣接一文字を含む。元file/manifest/イベントを上書きせず、legacyExtendedWindowSha256として検証・保全し、正しいcanonicalSpanSha256/開始/終端exclusive/source conventionを別sidecarへ追加する。診断理由/実PT/coverage/元pending/正式を変更しない。

Tool-only pmd_source_span_ascii.spanはLF・未解決Unicode escapeなし・boundary prefixがASCII/tabなしという今回sourceで確認した範囲に限定し、非対応入力を推定変換しない。正例4（単line/複line/末尾/変数名）と異常18（欠落/null/型/0/逆/empty/外/CR/NUL/escape/tab/nonASCII prefix）を固定literalから確認。これはProduct PT/coverageではない。

13652は元13620レビュー全二row/元13594 PMD source hash/当13604 caseを照合し、新半開区間と旧extended区間を別fieldに結合。13654は元XML/現source/元row hash/規約・offset・case不変更を独立確認、typed metadata異常を拒否する。元8試験/normal/静的checkの再実行0、実DB/JMS/HTTP/FS/native/Root/VM操作0。独立metadata工具以外の製品/Fixture操作は起動しない。

全106候補を是正済みにせず、当旧二collectorの現二rowだけ是正する。全YKT1819は他consumer/旧出力contract未照合のOPENを保持。refs3353/pending2492/raw6247/corr3194/原WBS/995旧runtime/予算受入/正式1964-53/17-190/工数null/QA051final/全actualHOLD・原本保全不変更。通常群/報告/commitで止まらず、fresh残10以下/取得不能で保全。
