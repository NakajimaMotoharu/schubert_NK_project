# PG6264 Outbox失敗所有 独立PT仕様（未実行）

Program NK-MSG-002、主WBS-P006-02、参照P006-04/F03/P018-05費0。RD MQ006008/ASY001・UI213241242・SS324332354/SSC320、BUG1566/1567・YKT1323/1324。設計だけmain131ce995e公開済。最初の赤sourceはcurrent97dd全Main同byte＋新Test一を予定、source commitは実行beginで固定。赤の失敗/未実施と旧全体成功は混ぜない。

新 `api.messaging.outbound.OutboxFailureOwnershipTest`、実行JUnit6件、matrix入力は件数へ加算しない。入力は接続しないJDBC/JMS interface proxy、固定Clock/UUID、SS323の256byte header＋QWKREQ01 DATA64byteをoffset/lengthから手組みした独立golden。production codec/対象methodをexpected生成へ呼ばない。全proxyは呼出counterと同Throwable identityを独立保持し、未定義呼出をAssertionErrorで拒否する。実DB/VM/Root/current/cohort/権限/OS資源の操作0。

| Test ID / method | 入力・操作 | 独立期待値 |
|---|---|---|
| PT-IDEM-FAIL320001 / fail320001NonfatalJmsPrimaryCannotHideCleanupError | valid golden OutboxEntry、getSessionModeがRTE、owned context.closeがError | 同じcleanup Errorが直接伝播、元typed primaryはsecondaryへ保持、causeは元RTE、close1・stage/commit/rollback0。普通send retry型に落とさない |
| PT-IDEM-FAIL320002 / fail320002UnreturnedJdbcSetupErrorClosesExactlyOnce | providerはnonnull接続を一度返す、setAutoCommit(false)がSQL/RTE/Error、close正常、dispatch起動 | primary各同一、close1・setAutoCommit1、prepare/claim/commit/rollback/JMS0。SQL/RTE旧期待も維持 |
| PT-IDEM-FAIL320003 / fail320003JdbcSetupCompoundFailuresPreserveIdentity | setup SQL/RTE/Error×close SQL/RTE/Error/同一Throwable | primary Errorは同一、nonfatal primary×cleanup ErrorはそのError同一、それ以外は元primary保持。distinctだけsecondary1・same自己suppression0、close1・未claim |
| PT-IDEM-FAIL320004 / fail320004RollbackCompoundFailuresNeverSelfSuppress | setup成功→最初のprepareがSQL/RTE、rollback SQL/RTE/Error/同一Throwable、close正常 | 一回rollback・一回close、型順位とidentityは上記、prepare1・commit/JMS0。callback/TWRの期待を実装結果へ合わせない |
| PT-IDEM-FAIL320005 / fail320005JmsFatalPrimarySurvivesEveryClose | getSessionMode Error×close正常/RTE/Error/同一Error | 元Error同一・distinct secondaryだけ保持・close1、stage/commit/rollback0。既IDEM010-R04の正常性を独立小fixtureでも維持 |
| PT-IDEM-FAIL320006 / fail320006NormalSendCommitsAndClosesWithoutRetry | fully valid literal golden、全JMS port正常 | body/property/destinationが明示vectorに一致、stage/send1・commit1・rollback0・close1。致命/再送を正常経路へ捏造しない |

PT_DEFAULT：自分の通常有限fixtureだけで副作用はメモリcounter。proxy入力は本scopeのpublic/package-local契約を通し、反射でprivate fieldを書換えない。拒否された操作の探索/再試行/代替経路ではない。プラットフォーム拒否が出た場合は当処理を再試行せず保全する。

PG6264は新6＋既定enum/codec/storageの12=宣言18/8suite、Main不変更のpurpose-redを一回予定。未実装機能ではなく既実装違反の再現なので修正前BUG登録済。結果が揃うまで件数やF数を予測で埋めない。

PG6266は是正二Mainの新6＋既定12＋OutboxDispatcherTest19/OwnedOutboxDispatcherTest5/WebLogDispatcherTest9=宣言51/11suiteを一回に集約予定。case名・宣言を実ファイルから検査し、全六format/compile/型null/警告/staticと同source原XML/六Jar/全8511667/二owner差分の独立資格を要求する。coverageは実測のみ、global100や実native成功を事前宣言しない。全体source宣言は新6追加で4040/607見込みだが、実inventory確認/必要全体真正0/全artifact照合前はPASS0。

最初に元PG6244/session1795の真正終端とPG6250原4034資格を閉じる。そこまでMain/Test freeze、新赤/製造の先行発行0。以降command、OS/JDK/tool、時刻/source、終了code/全XML、actual/期待、coverage、関連BUG/SS、公開hashを各run begin/manifestと実行結果に保存し、この仕様の予定と分離する。failed/flaky/skipped/not-runをPASSへ算入しない。

群1520開始.5/2/6pp固定、1490旧残との重複0。正式1964/53・17/190・工数null・QA051final・PTALT対象不明/代替0・実VM等HOLDは維持。通常purpose-red/PG/限定PT成功で停止しない。
