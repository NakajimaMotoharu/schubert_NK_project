# PG304 実backup工具実行 PT仕様書（実装前）

NK-OPS-001 BackupArchiveProcess、RD BAK/BKO/OPS009/UI251/SS341 §6・343、D04/05。専用backup UIDで固定pg_dump/pg_restore-list、rootで固定tar/ageを実行し、PGUSER schubert_backup/PGHOST loopback/PGPASSFILE保持fileだけ供給する。passwordをargv/envへ載せない。file adapterが各保持directory/file能力とowner/ACL/namespaceを先に検証し、全子terminal/stdio close前に能力を閉じない。実pathを公開・logへ出さず、source参照は親PIDの保持FDへ限定。内容生成だけでfsync/publish/manifest/DB成功/世代整理を代替しない。

PT-OPS-ARCHPROC001～008: 001 独立literal argv/clear environment/役割/command順、002 保持FD/名前allowlist/null/入力snapshot、003 各process exit/timeout/interruptionと終端不明非成功、004 全stdio取得/write/close/process terminationのknown/unknown compound、005 tar→age pipe・平文credential artifactなし・raw stdout/stderr discard、006 専用UID/rootUID主体・DB list検査・公開path不正拒否、007 並行独立実行/各owner再利用なし、008 実native toolsへの公開fixture暗号archiveと独立復号/一覧（実DBdumpは別VM経路）。全期待argv/結果はSS literalと独立tool結果から作る。

固定工具の30分deadlineは全process共通、失敗時は残った子へTERM要求後5秒terminal確認、未終端なら起動成功にしない。Process強制killや原本削除を成功へ読み替えない。stderr/logへ秘密archive filename/本文を収集しない。実backup生成bundle・DB確定・7世代・fullmorning/実NKは後続必須、全件not-run/合格0。129へcommand/環境/対象commit/結果/coverage/hash/障害を記録予定。
