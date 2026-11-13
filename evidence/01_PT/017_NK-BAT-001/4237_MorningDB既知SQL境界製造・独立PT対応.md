# Morning DB既知SQL境界製造・独立PT対応

NK-BAT-001/WBS-P017-01.03/P017-02.03、OPS009/DAT009/UI251、SS332/341/343/354 SSC341（origin/main03794704417）。BUG2852/YKT2359。対象MorningDatabaseSession known20捕捉と所有connection close/closeReplace。PT-MDB-CAT341-001～012の独立object/固定catalog/型優先/全資源後条件をSS354に定義済み。期待値はproductionを呼んで作らず、SQL・Batch・checkedIO・unknownの型と固定Error identity/固定message/close回数から決める。

本小群は既追加source/Test/static .6/1.8/3.6のうち、PG＋GJF/Checkstyle＋既20site/inverse/全literal不変の.3/.9/1.8だけ。残.3/.9/1.8は独立Test source・必要静的資格として残す（新規費二重加算なし）。製品Mainは一classのみ。outer executeでknown SQL graph内Errorが伝播する際primaryも実Errorへ更新してfinallyの既未知cleanupに置換させず、close/wipe/Session失効を維持する。他のtypedIO/unknownやSQL/role/TX/owner/lifetimeは既動作を保つ。

原20siteの公開sourcehash/行/捕捉型はPG29726。whole元MorningDatabaseSessionTest65と関連owner/DB全回帰の実行前提はHOLD、method抽出/新fake authority/DBやRoot・実運転probeは行わない。GJF/Checkstyleはsourceだけ。transitive Root/actual4 binaryを読むcompile/static実行をせず、NullAway/PMD/SB/実PT/coverage/実所有postは未実施として残す。本段のsource是正をPT PASSやPG全完了、451、190、IT/STへ算入しない。再試験時は固定source/runで原whole65＋承認済み追加故障・正常境界・終了依存を対応させる。
