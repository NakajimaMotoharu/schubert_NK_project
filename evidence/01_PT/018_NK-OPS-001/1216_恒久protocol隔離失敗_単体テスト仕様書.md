# 1216 恒久protocol隔離失敗：単体テスト仕様書

Program NK-MSG-001/NK-WEB-002、RD MQ008/010・UI231、SS321§7/322§11/352、PG-D442/BUG1494/YKT1254。上位SS322（main f6d9fe71b行180）により、恒久protocol判定後の隔離失敗はrollbackが正常でもACKせずexitが独立期待である。通常受信/業務一時障害のretryと混同しない。

| Test ID | class/method | 入力 | 独立期待 |
|---|---|---|---|
| ISO001/002 | api.messaging.inbound.FatalIsolationConsumersContractTest.iso001/002Sync* | wrong JMS type→隔離metadata readでchecked/Runtime、rollback正常 | Sync四contextのreadyfalse/fatal1/CommittedFatal0/business0、metadata読取1/rollback1/commit0、次の全context callbackで読取/再rollbackなし |
| ISO003/004 | 同.iso003/004Question* | 同上 | FIFO Question停止、同じ固定期待 |
| ISO005/006 | 同.iso005/006WebLog* | 同上 | WebLog停止、同じ固定期待 |
| ISO007/008 | web.messaging.ReplyFatalIsolationContractTest.iso007/008Reply* | 同上 | Web reply readyfalse/terminaltrue/fatal1/CommittedFatal0、read1/rollback1/commit0、次decode0 |
| ISO009 | protocol.transport.FailedJmsIsolationExceptionTest.iso009PrimaryAndProtocolAreRequired | primary/protocol各null | constructorでNPE拒否、NPEを正常catchする実装なし |
| ISO010 | 同.iso010SameNodeIsRetainedWithoutSelfSuppression | 同じPermanentProtocolException二引数 | cause同identity/追加suppressed0/原例外不変/固定非機密diagnostic |
| ISO011 | 同.iso011EqualsTrueDoesNotHideDistinctProtocolIdentity | equals-trueの別primary/protocol | cause primary同identity、suppressed protocol同identity一つ、equalsでdedupしない |
| ISO012 | 同.iso012DisabledPrimarySuppressionCannotHideProtocol | suppression無効primary/別protocol | primary不変でもwrapperのsuppressedへprotocolを保持 |

Test IDの正式prefixは`PT-JMS-`。各IDが一つの@Test/source methodへ一意対応する。API FatalIsolationFixtureとWeb test内の独立Fixtureは限定JMSContext/JMSConsumer/Messageのメモリproxyだけ。BUG1497でAPI test-jar公開の誤仮定を訂正し、module/POM依存を追加しない。plain MessageでBytesMessageではない恒久不正を与え、DLQ metadata.getJMSMessageIDから固定JMSException/JMSRuntimeExceptionをthrow、rollbackは正常復帰する。予期しないmethodはcounterを増やしてAssertionError、期待counter0もassertして、誤fixtureのError停止を正常PASSにしない。実Broker/DB/VM/Unit/current/原本Backup/鍵/permit/failed-cohort不操作。

各caseは開始readytrue/正規context数、初回の非commit fatal/業務未実行、次callback抑止、callback内close0と外側close全context数を検査する。期待値はproduction methodから生成せず、SS322/SS321から0/1と状態を明示する。固定Clockは2026-10-20T00:00Z。原3955/source2e3b・全850/1665は保存済み、test-only redのMain全同byteを独立照合する。

実command：clean Test sourceを固定→`pg5826_isolation_red.py red-api`一回（計15予定、実API失敗時Web二not-runは未合格）→未実施Webだけ`red-web`（API旧catalog1＋Web2等計10）。同じAPI再現は繰返さず、元fail/skipを改記しない。目的redはAPI六/Web二だけの予定assert失敗で、実source/actual class/Jar・正確な失敗ID・assert値を確認する。format、Maven3.9.12/JDK25.0.4、既NoTests/型null/SpotBugs設定は不変更、未実施static/coverageを0で補完しない。

是正PGは非commitの隔離失敗を型で区別して既外側fatalへ接続し、原protocol/隔離/rollback未確認を保持する。null/same/distinct/suppression無効、通常retry/隔離成功/未知rollback/Error/重複通知/所有closeをgreen前に追補する。元code2e3bの成功/core四100を新sourceの受入へ合算せず、新same-source実counter/必要全体を行う。source/branch/command/exit/XML/hash/環境は各private manifest、allowlisted公開結果だけGitへ保存する。正式/global100/native/CHR/451は別未完。

修正後限定commandは`pg5828_isolation_green.py`（明示66件/18suite、元54と新12、六module/実Main1666予定）。既InboundTransactionsPrimaryContractTest/ReplyIsolationPrimaryContractTestはsame/distinct原例外をwrapper causeとして保持しcommit0を確認、既SyncRequestListenerTest/ArtemisReplyConsumerTestはchecked/read/send/commit各phaseと未確認rollbackのcause鎖/独立protocol保持を補完し、method名/既case数を変えない。特にWeb未知rollbackも一回/commit0を実測する。期待は既SS322から定める分類と原fixture例外identityでありproductionをexpected生成に使わない。四counterは八coreについて実測を報告し、未網羅やnative/globalを補完しない。

原red照合：PG5827公開manifest f3de8b29bd903ed6d0e007e2bc43f8409a2670fd0e11905db76e7d9a0497a265、API-v2実13/6・六目的failure、Web-v2実10/7・二目的failure、全850source/実Mainは元2e3b同byte。redは成功PTへ算入0、旧API-v1のtry警告/七件とWeb-v1のfixture import/八件を元不合格として保持する。
