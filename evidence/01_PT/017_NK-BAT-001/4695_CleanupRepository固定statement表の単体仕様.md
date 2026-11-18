# CleanupRepository 固定statement表の単体仕様

NK-BAT-001。DAT-009、OPS-009、UI251、SS311 §7、SS332 §11、SS341 §3/7、451、PG-D-1186、BUG-3237、YKT-2683。CleanupRepository.prepare は既CleanupKind九値から、同じ九SQLのうち一文を取得する。可変SQLを組み立てず、borrowed transactionの所有も変わらない。

CLNQUERY001～009 は元wholeの全九。元CLNQUERY001は九kindに対するSQL全文・UUID・UTC cutoff・行上限を固定の手書き表と比較する。002～009は行数・保護数・空・上限前後・null・弁別されたSQL/RTE/Error・閉鎖順位・一回解放・借用Connection非変更を原独立fixtureのまま確認する。CleanupStepPortTestの原全九も同じ単一run。追加テスト定義0、元の期待値・SQL・Fixture変更0。

単体は既JDK JDBC Proxyのみ。実DB/cleanup/既原本や権限には接続しない。旧enum生成defaultとmapの未達、動的SQLの初回SpotBugs指摘は元証拠を保存する。新候補の全bytecode・未除外生counter・実行終端・ABI・SpotBugs SQL ruleを確認し、支援クラスや実環境の不足を保持する。
