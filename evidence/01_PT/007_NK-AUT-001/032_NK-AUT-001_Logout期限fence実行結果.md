# 032 NK-AUT-001 Logout期限fence実行結果

## 同source全体 PG448 full-v1

2026-10-04 07:56:25 JST、source c601c43b0c9a48906d153e87b23db943dfc29550、actual0/16:46、3082PT/FES0（81/154/213/888/724/1022）、6module XML件数一致・SpotBugs6zero・execution-data mismatchなし。safe018 PG448-logout-fence-full/manifest SHA256 62a80e0ef24b371862b4183952eac2bb7aa17843a8b33a3b0a91d6c56261d3c5、対象Auth3class全4counter0。WorkPG379/pg448-host全6actual classes/testclasses/XML/exec/site/static/JAR/runtime dependencyをbyte一致保全、source固定解除。BUG618/YKT437の当該境界/currentClock/fence/rollback/既存再送host再試験を完了。既存host残B1222/L3477/M567/C39、一般0102 proof化0・別source結果合算0、WebNULL期限/retry/native/CHR/正式run24は未完了。

## 修正後選択 PG448 expiry-selected-v2

2026-10-04 07:35:08 JST、actual0/02:46、69PT8suite（5/7/10/29/10/8）FES0/static6zero。AuthSessionRevocationService/LogoutInboxService/AuthenticationContextVerifierの3class B73/L234/M17/C3全miss0。独立4method＋既存null/fault/100再送/ADMIN、expiry±1µs/audit EXPIRED0102/ERROR同TX、同Message immutable0102・新Message0200、lock後Clock、先行TOUCH延長と保持User lock下の遅延認証拒否/TOUCH0、7 expired update/audit/Inbox/close faultrollbackを実証。修正sourceはHEAD c560e5f8＋API2source/2Test dirty、全filehash実行前後一致。log cf4de11bc7ea2fb289374869c2136b9c84c81f9ba65f75f87020fb72488cddee、全6actual byte pg448-expiry-selected-v2-frozen。safe007 PG448-expiry-selected-v2/manifest SHA256 cebb1a27d701b113301aa910279e33211b85394e62384ce90029a6300ad527a2、metadata-only XML（provider/秘密情報なし）。BUG618/YKT437限定是正確認、fresh同source全6/native/Web retry/正式未認定。

selected-v1もactual0/02:45/07:29:58、67PT8suite/FES0/static6zero/3class全miss0だったが追加意味試験前の別sourceとしてWorkPG379/pg448-expiry-selected-v1-frozen保存、log f31ae3adedccc28b71359ea001a8f60a34f458c08bd31d071fcd1125200b4090。v2へ合算しない。

## 修正前独立反例 PG448 expiry-before-v1

2026-10-04 07:25:25 JST、source HEAD c560e5f8e7deb67af6c5c9feca37fc3962b3d91c＋LogoutInboxServiceTest独立2methodだけdirty。実行commandはWorkPG379/pg448_expiry_before_v1.sh（Java25.0.4/Maven3.9.12/Linux7.0.0-38、隔離実PostgreSQL18.6、明示6module/no-am/各module canary/failIfNoTests=true）。actual exit1/01:13、実API2PT2F/E/S0、Web/Batch未実行。先行Protocol5/Storage7/Bootstrap10成功は全体成功としない。

| Test ID / method | 独立期待 | 実結果 |
|---|---|---|
| RERUN001-A/B / rerun001ExpiryBoundaryFencesAtomicallyAndPreservesErrorReplay | expiry<=nowの既定0102＋SQL revoked1/audit1/ERROR1 | wire0102だがrevoked0、最初の境界で失敗。後続replay/他境界は未完了 |
| RERUN001-C / rerun001CurrentClockIsReadAfterSessionLock | row lockを実取得した後にClockが2µs進みexpiry1µs超過、独立280byte0102 | 旧lock前nowにより0000、byte209 expected49/actual48。commit/fence後条件は未実行 |

Log SHA256 dbda036d301df589d4721474e466c3e14cf42846b89ee2a268719e8fd4e3c133。WorkPG379/pg448-expiry-before-v1.source-files.sha256は実行前後一致、実4module classes/testclasses/XML/exec/site/存在staticをpg448-expiry-before-v1-frozenへbyte一致保存。API静的/coverage受入は未実行、旧Web/Batch targetを当runへ流用しない。秘密provider出力をGitへ保存しない。

BUG618/YKT437/QA050/SSC171/031に対応し、before保存後にlogoutCurrent(Clock)→session lock下時刻→EXPIRED update/audit→既定Inbox ERROR同TXを修正中。旧Instant/ADMIN・一般0102とWeb0000/0200限定proofは不変更。現在selected-v1でAuthSessionRevocationServiceTest/LogoutInboxServiceTest/AuthenticationContextVerifierTestと6module canaryを検証中、未終了を合格にしない。修正source commit/coverage/全体fresh/native/Web retryは未確定。
