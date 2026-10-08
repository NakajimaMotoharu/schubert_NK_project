# PG595 保持Expiry原本・SKIP契約

P017-01.03既群.66/1.66/3.66pp継承、追加費重複0、NK-BAT-001/OPS009/DAT009/UI251/SS331341343/SSC125200。PT-OPS-MDB595001、MorningDatabaseSession.Session.beginExpiry/observeExpiry、四条件を新1PT内で検証する。

実隔離host DB、既独立failedBackup→Cleanup sixSKIP/TransferSUCCESS→verified後、別run・同営業日の保持Expiry SUCCESSをliteral SQLで作る。旧run cutoff=current+1秒、開始fixture midnight-10秒/終了-9秒、attempt1・target1/success1/failure0/byte17・expiry cutoff旧run-7日/before2/after1。独立oracleはこれらliteralから構成しProduction expected生成0。

正常resolverは実prior UUID/観測時刻を確認し固定原本を返す。currentはattempt2/SKIPPED/ALREADY_SUCCESSFUL/全count0/開始=終了+4秒、保持auditは旧literal全column不変。子callbackは実advisory取得/ack解放、0receiptだけ受入、30拒否でrow変更無し。不正営業日の原本、取得IOException、null返却はそれぞれ固定拒否/プログラミングnull失敗を確認、旧/current committed全row不変・最終close/advisory非所有。日付/run/idは旧PG590592594と独立seed37～40。

command `bash tools/quality/vm/050_s1/pg587_access_returns_v1.sh <固定HEAD> PG595`、新only/private・同main1600byte・旧V5exec隔離/append0・Access9/MDB30=39期待。JDK25.0.4/Maven3.9.12/PG18/Flyway28/Spotless/NullAwayWerror/Spotbugs/JaCoCo0.8.15、実結果/coverage/hash/source/runは実後追記。BUG878/YKT647初回原因品質保留・formal24/1964/53維持、VM完了run/通常DONE/退役/停止を再発行0。
