# 1300 API JMS close選択v2：旧oracle六件不合格を保全

仕様1297/SSC314、source **19c81fcab4e58d3d24f64780c2f7dd5c4dda3912**、元exec25471/pg6144-api-jms-close-selected-v2。2026-10-20T18:19:29.603303Z～18:28:06.209823Z、真正exit1/Maven1/phase[0,1]、固定入力。JDK25.0.4/Maven3.9.12/通常自己所有host、commandはPTPRE038/pg6144工具。元job再発行0・新sourceへ成功の流用0。

実 **1029件/174suite、failure3/error3/skipped0**。API1024を実行し、guard5を含め1023成功は当run内の限定実績であって全体合格ではない。予定1950/320の残 **921件/146suite not-run**（Web/batch）。API失敗により六targetのreportは未生成・**未測定**、manifest placeholder0/0を実0%/100%にしない。前protocol/storage/bootstrap型nullSpotBugs0だけ確認、全六静的成功と認定しない。

不合格はBUG1554/YKT1312へ修正前起票した旧六Test（Question core004/008、Sync closeIsIdempotentAndAggregatesAllContextFailures、WebLog closeIsIdempotentAndStartupPreservesCloseFailure、Remainder syncDrainPromotesLaterErrorButAttemptsAllFourContexts/completeProfileClosesInReverseGroupOrderAndPreservesDistinctFatalIdentity）。未確認close後のno-op正常期待がSS342SSC158/SSC314に反する。新ApiConsumerCloseOwnershipTest **6/6成功**、ApiBrokerContextsTest **8/8成功（新1を含む）**は元XML確認済みだが、全体不合格を取り消さず新sourceへ算術加算しない。

私有PG379/pg6144-api-jms-close-selected-v2/：begin.safe.json SHA **fa22e91d649f6ba81f880aa217d85cc4333b3aea68deac4a8c21acabeab850a5**、source.tar **0f0684add8c554d1031edc37a0ebcecc3fe55a1136ea25f8575ffe336ba6d502**、manifest.safe.json **5fdac65eb5016b661eba722e4d19f4ac38e3b7bbbd4828591417b406aedc29cc**。原XML/log/Jar/actual sourceは保全、raw秘密をGitへ出さない。

是正は既六oracleの同一例外/再失敗・正常child再発行0のliteral countのみ。元v1 generic compile欠陥1551はこのrunで全Test compile済み、元失敗1298は保持する。未実行6146/6148はこの不合格sourceへ資格を付与しない。次はS3aのprovider/親owner実PGと併せた新source/新onlyPG6150の1955/321/全六静的・八target実四100で確認する。元全回帰再演でなく関連変更群の必要影響PT、S3b/native/CHR/全体/451/traceは別未完。正式/工数null/QA051final/PTALT未特定代替0・実環境安全HOLDを維持する。
