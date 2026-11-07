# 元process八起動の所有・終端sourceレビュー結果

sourcecd5c778/Main7aed、PG23020/23022独立0 manifestb59f5b36d2f1435c44555f2358c67f81047fd200cc4877da91e2230bf2b5c6d1。current29 hash/八ProcessBuilder・五class六method・既parse23010同byteを確認、metadata否定7。元Test/source/parser再演/実process start-destroy-wait-recovery/VM/native/Root/DB/FS0。全8はmethod-local Process所有、private external helperはexit int返却でProcess移転ではない。builderだけの構築と.start後のProcess所有を区別。

既五に加えInode.setAcl/ProcessExec008/StartupFileLock.external三つもfailure cleanup後の退出回収不足を同BUG2467/YKT2205へ追加確定。FileLock外部methodはexecutorがstart前に存在し、具体的な取得途中のgapはreader/writer。ExecDescriptorsはstart後にexecutor/reader取得でgap。正常wait/exit確認を失敗後条件へ転用しない。具体source修正は未実施・OPEN。

別BUG2468/YKT2206: flock通常fork形式五argvは親PID退出だけでcommand/lock終了を認定できない。installed util-linux2.41.3 primary manualのno-fork契約と二Java childのsame-PID Python exec sourceをread-only確認しhashを保存、guest版/実process treeは未測定。元argvをno-forkへ暗黙変更せず、parent回収とcommand所有/終了を別の是正条件とした。setfaclのdescendant有無を一律保証しない。

一次根拠は[Java25 Process API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Process.html#destroyForcibly())とinstalled primary manual（manifestにpath/hash）。終了要求が即時exitと同じではないこと、stream資源を明示解放すべき契約を記録する。これはSource契約レビューで、実job終了/安全操作の許可を追加しない。

後続source remedy条件: 取得前のowner準備・startからの全失敗scope、blocking stream/executor解放前の終了手当、有限post waitとUNKNOWN失敗、interrupt/primary/suppressedの保持、fork command側の取得競合/同run所有/退出・lock後条件。親だけのsource helper追加で全8やfork5をcloseにしない。既fixture入力を変える代替試験や元native/Test compile/runはHOLD。

477停滞点検: 通常PT31件の必要再資格とStorage132→82/全82個別理由は実成果だが新leaf0/正式不変。以後のgroup選定は未資格Production componentの現Code/既証拠へ戻し、独立した通常PTを優先する。当process source remedyを完了扱いせず残PGとして460/BUG2467/2468へ保持、技術的難しさを外部入力待ちや全体停止にはしない。438/whole94/正式1964-53/工数null/全HOLD維持。
