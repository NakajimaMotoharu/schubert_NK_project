# Web手動transaction secondary保持・rollback PT仕様（PG前）

Program NK-MSG-002/NK-WEB-001、class `web.logging.WebOwnedAttachment329Test`の一意対応：

| method | Test ID |
|---|---|
| owned329001DispatcherRollbackGraphSurvivesDisabledSuppression | PT-WEB-DISPATCH-ATTACH329001 |
| owned329002DispatcherCloseGraphSurvivesAndNonFatalRawSqlRemainsSame | PT-WEB-DISPATCH-ATTACH329002 |
| owned329003DispatcherDirectErrorRollsBackAndKeepsLegacyClosePriority | PT-WEB-DISPATCH-ATTACH329003 |
| owned329004RevocationRollbackGraphCannotSkipRemainingClose | PT-WEB-REVOCATION-ATTACH329001 |
| owned329005RevocationCloseGraphAndBothFatalGraphsKeepPrimary | PT-WEB-REVOCATION-ATTACH329002 |
| owned329006RevocationNonFatalAndDirectErrorPoliciesRemainFixed | PT-WEB-REVOCATION-ATTACH329003 |

原反例確定：元6612/dbb0a503b source固定、UTC2026-10-21T17:55:15.327283～17:57:35.609859、archivec819902db8ffc77ceba9ec1098da5a8dc61fcf805cb033b6dd535d43823138b1、実16/6 F5/phase0,0,1真正1/E/S/flaky0、原`PG6612-web-owned-original-red-v1/manifest.json` SHA060b6f31a3cfc873a575611c94ec78278fa35813970fe3f98f9c994273af19ceで事前五assertion一致・not-run2加点0。既006非fatal/directError優先は成功。次PG-D493の二Main接続、全六/旧Testbytes固定→green6614/39-11/原6616、現未実行。

実Test定義：WebOwnedAttachment329Test六method/SHA512991fd327f7b3b9924686179941bd8c9ebabb809718a9475e5d1f7be80d028。Main d48a13f4d・全旧Testbyte不変更、format39254終了0/管理三0/pyflakes0。`pg6612_web_owned_attachment_selected.py red`のnewonly6612/18-8、予定原16/6 F5/not-run2、四identity不一致とdirectError rollback0のcounter不一致を事前固定。identity比較はassertThrows(Throwable)の実際object==固定expected Errorで型も含めて検証し、その前にsource/prepare/transaction/send0前提assertを行う。green6614/39-11→原6616、いずれも現時点未実行。

具体化方針：同じowned Connection proxyを二programで共有するため、予定二classから`WebOwnedAttachment329Test`一class六methodへ集約する（TestID/期待値/六ケースscopeは不変更）。redはbaseline12＋新6＝18/8、Web停止時予測16/6/F5/not-run2。greenは新6＋旧WebLogDispatcher10/Revocation8＋WebStartup pure3＋baseline12＝39/11。constructor/JMS facadeはpure objectsのみ、replies pending0とsender到達0を独立確認する。

485実物で主担当はWebLogDispatcher=WBS-P006-04、RevocationRetryCoordinator=WBS-P015-05、共通口P018-06。これらはP006-03のREQUEST producerと同一WBSではなく、共通費と個別consumerの配賦を推測しない。新codeは先行6608/6610の原qualification終了まで変更しない。

既群ORDINARY_JDBC_MAPPER329/開始.5/1.5/4pp不変、原-v4/実配賦/N/T null。BUG1592/YKT1345/1348、SS312329330/324/332/354。対象WebLogDispatcher.transaction/closeAfterFailureとRevocationRetryCoordinator.transaction/combine。既SQL raw58は無条件非該当でなく、最終receiver（WebLogReplayWorker/RevocationRetryWorker）が分類するまでgraphを保持する責務を確認する。実Root/VM/current/cohort/permit等HOLD解除0。

## 必要PGの事前点検

両manual ownerのinline addSuppressedは、suppression無効primaryに対するsecondarySQL内包Errorを失い得る。common pure WebStartup attachmentを再利用する場合、そこからErrorが先行伝播しても残Connection.closeを必ず行う。WebLogDispatcherは既outer finallyが保護している。Revocationはrollback後のcloseが単なる後続文なので、rollback合成をtry/catch(Errorを失敗として保持)/finally closeで保護してから共通口へ接続する必要がある。close後のcombineがErrorをthrowする場合も、既close実施済みで成功は返さない。

WebLogDispatcherの内側catchはSQL/RTEだけでdirect Error時rollbackを試みない。SS312329のowned transactionをErrorにも適用し、直接primary Error＋rollback Errorはprimaryを保持する。非Error primary＋直接rollback Errorの既secondary優先と、直接close Errorを優先する既component規則は維持する。同一Throwable self-attach0、rawSQL/unknown型と既suppressed配列（通常有効時）の保存、JMS send/claim/commit/backoff/SQL literal/worker lifecycle・権限の変更0。

## 六Testの独立oracle（予定二class）

PT-WEB-DISPATCH-ATTACH329001：claim prepareでsuppression無効Runtime、rollbackSQLのcause/next内包Error→同fatal、primary graphにもfatalがある場合は既primary graph優先。prepare到達1/getAutoCommit=false前提/rollback1/close1/commit/send0。

002：同primary＋closeSQL内包Error→同fatal/rollback1/close1。SQL同一Throwable/非fatal循環は元SQL identityとsecondary契約を保持し、未知Runtimeを成功化しない。

003：direct primaryErrorはrollback1/close1で同identity、rollback Errorでもprimaryを保持。別direct closeErrorは既close優先、同じErrorの再throwはself-suppression0。修正前はdirectErrorのrollback0を独立counterで反例化する。

PT-WEB-REVOCATION-ATTACH329001：connection返却直後setAutoCommitにsuppression無効primary、rollbackSQLに内包Error→同fatal、close1まで済んだ後に伝播。primary graph fatalを持つ場合も既優先保持、wire送信0。

002：同primary＋closeSQL内包Error/rollbackとclose両側fatal、同scopeの既優先とclose一回/rollback一回を保持する。

003：非fatalcycle/同一Throwableは原因・suppressedなし固定RevocationRetryException、directprimaryError/secondaryErrorの既primary優先、結果成功/remote送信0。

PT_DEFAULT、全てpure interface proxy/公開constructor fixture/固定時計・canary buffer、DataSourceは外部へ接続せず、JMS senderは到達したらassertionで拒否するfixture。実DB/VM/鍵/認証回避/外部サービス操作なし。各requireTransactionのgetAutoCommit前提と目的到達counterを先にモデル化し、BUG1597を反復しない。旧Main上で予定反例を元XMLから独立確認後、必要二Main/全Testbyte固定/旧自己所有DB・JMS domainsをgreen→原同source資格→115site map/まとめ必要全体/F03/trace/残PGPTへ。具体Test名/数/run/hashは宣言確定後に固定し、未実行は合格にしない。
