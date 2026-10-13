# PG2504 STRICT終端・同run参照 変更Main単体仕様

NK-OPS-001／BrokerJournalEvidence.fields・MorningDatabaseSession.currentRunReference/Session.cleanupReferences。SS321331341343・SSC133134200、PG-D416417、WBS-P017-10/P017-01.03、N04/N05参照費0、0650着手予算0.5/1.5/4ppを保持。新Main候補をcdbc/PG2428の正式・native資格へ流用しない。

PT-BJ2478-001..004及び既Broker三methodを変更Mainへ再実行。期待=STRICTの余剰JSON/comment/BOM等は同じ拒否、全metadata/最大byte/cursor/time/UTF8/独立canonical/raw SHA/provider障害・復元/null/例外/秘匿不変更。固定Gson2.14.0 SHAとPG2498の独立17contractを根拠に、peekによるEOF検査を省略しない。期待を変更Productionから作らず、既golden/固定vectorを保持する。

PT-MDB2504-001／mdb2504001：fixture runUUID25040001、cutoff2037-01-09T15:00Zを固定。lookupは同UUID＋2037/2040の二観測時刻で同じ元dataを返す、foreign UUID25040002は固定秘匿IOException、factory run nullとid nullはnonnull拒否。observedを別run/cutoff導出やauthorityへ使わない。公開Sessionの実owner/DB/transaction/readbackは別既存契約のまま。reflection/秘密値/rawSession/native権限捏造0。

実command=`python3 -B tools/quality/pg2504_strict_reference_selected.py`（固定PYTHONPATH）。clean固定新snapshot・fresh PG2504-selected-v1、専用LAN JDK25.0.4/Maven3.9.12/PG18/Gson2.14.0。全同snapshotの五依存はcompile/test-compile/JAR installのみでPT加点0、私有repositoryを使いshared cache書込0。batchは指定二class・計八methodだけ必須実行、skip/noTests迂回0、format/compile/static/coverageと入力hashを検査する。Broker四counter100、MDBはpurefactory対象のみ限定で全体100とはしない。actual終了/source/各counter/静的/証跡は取得後追記、必要fresh全体・新署名runtime/native/451は別未完。

## BUG1242/YKT1008 是正前検出・scope訂正

上段の「Broker四counter100」はclass全体について選択hostだけで要求できる条件ではなかった。旧文を失敗仕様として保持し、新only v2は変更fields（L/M/B）及びcurrentRunReference/同lambda（L/M/B、factory自身はcondition0）を全網羅必須とする。全classのCLASS/L/M/B100、native inspect/inspectStopped、global451は同新sourceの全回帰・実native後の終了条件として一切緩和しない。

v1 sourcea79/client73373：Maven0/依存compile0/指定八PT/FES0/静的batch0/入力不変だが、工具outer1。Broker全体L147/181 M11/13 B97/98・native二method/34line等未実行。これは新codeの外部仕様違反ではなく選択gate範囲の誤り、旧failednamespace/manifest/XML/logを保全し工具成功へ補完しない。新v2は変更method scopeの欠落/未知/missed/false/0covered/branch欠落/新branch隠し七反例を拒否し、nativeNotRun/wholeRegressionNotRun/wholeClassFour100Accepted=falseを常に明示する。関連915 BUG1242・916 YKT1008を先行起票、修正commit/actual新v2後記。
