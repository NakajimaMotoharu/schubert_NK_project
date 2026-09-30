# 283 Expiry通常再開・元成功参照（実装前）

NK-OPS-001/NK-BAT-001、CleanupWorkerRequest.Expiry / CleanupExpiryExecution.mq、RD OPS009/DAT009、UI251、SS341§9/11・343§6.17、SSC117/BUG351/YKT280。

PT-OPS-EREQ005：独立literal NKEXPIRYSKIP1 golden（今回row43/attempt2、元row42/attempt1、元開始00:00:01Z/終了00:00:02Z、今回開始00:00:03Z）。encode/decode値・input消去・通常profile相互拒否。境界null/欠落/順序/未知/同row/未来終了/同attempt/不正時刻・size1025を拒否。

PT-OPS-ESKIP001：実PostgreSQL固定DDLで元SUCCESS audit(before3/after1/target2/success2/failure0/bytes200/cutoff原本-7日)と今回SKIP全0を独立SQL fixtureで作成。実callerが元完全handleだけaudit.readし、今回rowも別readback、fresh selected0だけ成功。元全列不変、mutation SQL0、purge0。元ended/数量/cutoff/status/null/現在row/count/reason改変・selected1は拒否。期待値はliteral SQL/固定時刻から作成しproduction methodで生成しない。

実行：固定JDK25/隔離m2、Batch＋依存test/static/coverage。対象commit・結果・coverage・evidence/hashは実行後284へ記録。native fresh broker/ExpiryはS2接続後に別実証、未実行をPASSへ算入しない。現在NOT-RUN、coverage未採取。
