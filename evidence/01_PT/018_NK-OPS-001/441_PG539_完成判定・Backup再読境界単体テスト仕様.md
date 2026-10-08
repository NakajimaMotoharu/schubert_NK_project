# PG539 完成判定・Backup再読境界単体テスト仕様

NK-BAT-001/NK-OPS-001、RD BAK001～008/BKO001～008/OPS009/DAT009、UI251、SS332341343354/SSC067187200203/451487。WBS-P017-04既0.5/1.5/3.5＋P017-12.01子0.67/1.67/3.67＝群低1.17/標準3.17/高7.17ppを0041 event/09:05:46JSTでfixture編集前固定、親P017-12/他子/N/K01重複0。元全体残90.9/269.8/642.6未較正、実token未知を共有枠から推計0。

| Test ID | class/method・入力/操作 | 独立期待値と算出根拠 |
|---|---|---|
| PT-BAT539001 | BackupBundleCompletion.complete：独立golden実fileとfixture専用PostgreSQL。実write commit直後、別admin接続で二SUCCESS rowのended_atを04.987654Z→04.987653Zへ変更 | 新transactionで有効だが保存戻値と異なる再読を拒否、BatchRepositoryException固定diagnostic/原因null/正常返却0、commit1/rollback0・読取TXはcaller所有/Connection未閉鎖。独立SQLは全二row/正しいcounts/04.987653Zを確認、artifact全原byte不変。実VM/原本DB更新0 |
| PT-PARENT539001 | MorningCompletionEvidence ctor：BackupBegins異run・DB/Config異handle、Expiry targetのBackupreceipt差、SUCCESS envelopeに実30receipt | constructorはIllegalArgumentException、dataをauthorityへ変換0。固定UUID/step/row identity・Outcome/manifest/receiptのSS因果関係を独立vectorへ対応 |
| PT-PARENT539002 | 完成判定clock02:00:30/02:01:30、Cleanup PROTECTED WARNING/正規10、Expiry WARNING正規10/誤0・SUCCESS誤10・FAILED | 各処理実終了より前なら固定IOException/原因null。Cleanup又はExpiryだけWARNINGでもWARNING完成、Backup成功を唯一条件へ変更0。Expiry状態/receipt不一致・FAILEDをconstructor拒否、期待文字列・UTC時刻・固定enumを独立明示 |
| PT-PARENT539003 | verify既定原本lookupをcleanupReferencesの実callback port経由で同UUID/foreignUUID各1回要求 | 真正runUUIDだけ固定RUNを返却、foreignに固定IOException/原因null、lookup到達2・cleanupReferences到達1。callbackを使わないproxyでcoverage漏れを隠さず、実DAOの要求境界を独立fixtureで確認 |

sourceMain変更0/承認SS/Currentbaseline変更0、test fixtureへのSQL操作は専用temporary synthetic DBだけ。VM全businessidle・native9/保全原本Backupは維持し二重起動0。既対象のnegative/null・所有/並行/再送群と新四PTをbatch全suite、依存storage/bootstrap全非空suiteでまとめて回帰。依存2moduleのcurrentbyteをreactorでcompileし古いM2 SNAPSHOTを実装sourceとして認定0。build/NullAway/SpotBugs3module・XML/FES・四counterを同sourceで照合、全6formal/native/CHR未実行は合格算入0。

実command=bash tools/quality/vm/050_s1/pg539_completion_pt_v1.sh <fixed commit40>、JDK25.0.4/Mavenwrapper/offline既repo、new-only私有work/pgpt-runs/PG379/pg539-completion-boundary-selected-v1.{log,exit,source,started,completed,source-files.sha256}、全XML/coverage/static/jarを保存後safe manifestへTestID/actualexit/source/hash/counterを対応。PG495/PG533別source成功を当実行の全合格へ加算0。まだ未実行、仕様が期待値と異なれば修正前BUG/YKT、未達は未達のまま保存。
