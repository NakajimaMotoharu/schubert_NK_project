# C03 PostgreSQL設定・当source個別criteria監査

WBS-C03、SS342§6/§9・UI212/253・RD SYS/DAT/PER、主費.25/.6/1.5週次枠ppを既計画のまま群1752で固定。実Unit/TLS/権限操作とProduction追加は元costScope対象外。全Main/既Test/Current/設定不変更、PGは既実装の全文/依存/独立oracleを点検し正しいため修正不要と判断した。新規PTの起動は0。関連PG-D187/SSC069/BUG208209の旧是正を取り消さない。

## 正本・対象・独立期待値

fetch後のorigin/main=8b91944df5820535e23ba2469740f1c0aa94c447。SS342§6の32directive・loopback専用/port5432/max40/各buffer・work memory/WAL/checkpoint/deadlock/SCRAM/ssl offと、logging具体化（SQL/parameter本文抑止と運用event）を独立literalへ転記した。HBAはlocal postgres peer、六role両loopback＋InspectorIPv4だけ、末尾両全域rejectの順16行。role timeoutは六role各3＋Inspector明示2=20設定、Inspectorのidle未設定を設定済みとしない。

主対象は `src/deployment/postgresql/postgresql.conf.template` / `pg_hba.conf.template` の二file（485の全ownedArtifactsと一致）。shared参照はAPI provisioning/001_roles.sqlとPostgresDeploymentTest、追加の共通製造/PT費0。全四fileを当PG6930/source e7d64fda2453e906ee6ccc5fe718e5c29841e4aaのarchive入力・git blob・現在byteへ厳密一致させた。正本design hashもmanifestへ記録し、実配備DB/鍵/原本を読まない。

## TestIDと当元証跡

|Test ID|method|独立期待値・実後条件|
|---|---|---|
|PT-OPS-PGCFG-001|literalConfiguration|32key/value・重複無し・全体一致|
|002|nativeConfiguration|PostgreSQL18自身の-C/実終了0、unit換算（2GB→262144等）・on→pglzを既固定literalで比較|
|003|literalHba|順序16行・role/address/auth完全一致|
|004|nativeHba|自己生成DBのpg_hba_file_rules列と順序・parse error無し・元HBA復元|
|005|roleTimeouts|自己生成DBの7role/20明示timeout・Inspector idle無し・SQL array解放|
|006|invalidConfiguration|未知GUC/不正quote非0、公開bind/SQL本文/欠落/重複/空/nullの独立negative|
|007|invalidHba|不正authのnative parse error、trust/md5/remote CIDR/末尾reject欠落を不一致として検出、元HBA復元|
|008|isolationAndEvidence|target内新TempDir・loopback URL・元HBA不変・rawDBlogコピー無し/reload無しの固定safe trace|

002～008のprefixもPT-OPS-PGCFG-。元4222原資格728682a9/同case692fcd4d内のPostgresDeploymentTest八methodへ、当Test byte SHA256 b3d2090ca93a263e77011c16cd4ac915faaa8da4f972270533a3a3d45a0f11ccと各method hash/実XML hash/PASS_ORIGINAL_XML/sourceを一意join。現在jobを再起動せず元成功だけを参照した。資源のBeforeAll/AfterAllは今回是正済みApiLogDatabaseFixtureと整合し、元全体FESflakyNotRun0/六static0に属する。

## 個別criteriaと結果

read-only `python3 -B tools/quality/pg6946_c03_current_criteria.py`、既full PYTHONPATH、exit0。公開 `evidence/provisional/PG6946-c03-current-criteria-v1/manifest.json` SHA256=9695e383d3af6f227e9d01fecc37063faa7f304ad463c8090a7368d808a2546c。contract/scope/qualityのローカル根拠3件を確認、現artifact二つ/共有参照/TestID八つ・正本/原hashを内包する。

管理checker四件/pyflakes0（Production PT加点0）。設定parserは固定文字列を比較するだけでPostgreSQL parserの代替ではなく、native parseの実証は既当002/004/006/007に限定する。初回未完成toolの構文検査はunpacking記法誤りでimport前失敗/PT0/公開manifest無し。初回compile段階として保持し、括弧修正後に管理四/pyflakes0・原読取0を実施した。実装済み設定/既試験/元成功は変更していない。

これはCURRENT_CRITERIA_EVIDENCE_READYでありcanonical WBSの新規ACCEPTEDではない。歴史的source7fffの17受入へ当e7の別source一件を混ぜず、追加受入数0/工数null/正式1964/53を維持。後続の同source個別認定・canonical全体整合へこの3件の根拠を参照できるが、本書だけで18/190へ加算しない。

## 残存risk・非該当

当readerはDB/VM/process/Unit/配置/reloadを一切操作せず、実環境のSHOW/remote接続拒否/active設定drift・primary error MESSAGEの全秘密非出力は未確認で別runtime gate。設定templateは宣言型でJava四counter適用無し、Testの管理4を実測coverageへ足さない。既SQL失敗/old native/Current baseline/QA051final/PTALT0/全HOLDは不変。C03確認をPGPT全完了又はIT/ST完了へ読み替えない。

別候補のNK-CHR-001は旧41/41/四100成果を020の正本で確認できた。Current/NK実互換とは別で、同じ成功の確認目的の再実行や既基盤への新規format要件は追加せず（BUG1411/YKT1175の境界を維持）、新規成果として加点0。次は他の独立CONFIG criteriaを当元試験と照合する。
