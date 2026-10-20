# 1216 恒久protocol隔離失敗：単体テスト仕様書

Program NK-MSG-001/NK-WEB-002、RD MQ008/010・UI231、SS321§7/322§11/352、PG-D442/BUG1494/YKT1254。上位SS322（main f6d9fe71b行180）により、恒久protocol判定後の隔離失敗はrollbackが正常でもACKせずexitが独立期待である。通常受信/業務一時障害のretryと混同しない。

| Test ID | class/method | 入力 | 独立期待 |
|---|---|---|---|
| ISO001/002 | api.messaging.inbound.FatalIsolationConsumersContractTest.iso001/002Sync* | wrong JMS type→隔離metadata readでchecked/Runtime、rollback正常 | Sync四contextのreadyfalse/fatal1/CommittedFatal0/business0、metadata読取1/rollback1/commit0、次の全context callbackで読取/再rollbackなし |
| ISO003/004 | 同.iso003/004Question* | 同上 | FIFO Question停止、同じ固定期待 |
| ISO005/006 | 同.iso005/006WebLog* | 同上 | WebLog停止、同じ固定期待 |
| ISO007/008 | web.messaging.ReplyFatalIsolationContractTest.iso007/008Reply* | 同上 | Web reply readyfalse/terminaltrue/fatal1/CommittedFatal0、read1/rollback1/commit0、次decode0 |

Test IDの正式prefixは`PT-JMS-`。各IDが一つの@Test/source methodへ一意対応する。API FatalIsolationFixtureとWeb test内の独立Fixtureは限定JMSContext/JMSConsumer/Messageのメモリproxyだけ。BUG1497でAPI test-jar公開の誤仮定を訂正し、module/POM依存を追加しない。plain MessageでBytesMessageではない恒久不正を与え、DLQ metadata.getJMSMessageIDから固定JMSException/JMSRuntimeExceptionをthrow、rollbackは正常復帰する。予期しないmethodはcounterを増やしてAssertionError、期待counter0もassertして、誤fixtureのError停止を正常PASSにしない。実Broker/DB/VM/Unit/current/原本Backup/鍵/permit/failed-cohort不操作。

各caseは開始readytrue/正規context数、初回の非commit fatal/業務未実行、次callback抑止、callback内close0と外側close全context数を検査する。期待値はproduction methodから生成せず、SS322/SS321から0/1と状態を明示する。固定Clockは2026-10-20T00:00Z。原3955/source2e3b・全850/1665は保存済み、test-only redのMain全同byteを独立照合する。

実command：clean Test sourceを固定→`pg5826_isolation_red.py red-api`一回（計15予定、実API失敗時Web二not-runは未合格）→未実施Webだけ`red-web`（API旧catalog1＋Web2等計10）。同じAPI再現は繰返さず、元fail/skipを改記しない。目的redはAPI六/Web二だけの予定assert失敗で、実source/actual class/Jar・正確な失敗ID・assert値を確認する。format、Maven3.9.12/JDK25.0.4、既NoTests/型null/SpotBugs設定は不変更、未実施static/coverageを0で補完しない。

是正PGは非commitの隔離失敗を型で区別して既外側fatalへ接続し、原protocol/隔離/rollback未確認を保持する。null/same/distinct/suppression無効、通常retry/隔離成功/未知rollback/Error/重複通知/所有closeをgreen前に追補する。元code2e3bの成功/core四100を新sourceの受入へ合算せず、新same-source実counter/必要全体を行う。source/branch/command/exit/XML/hash/環境は各private manifest、allowlisted公開結果だけGitへ保存する。正式/global100/native/CHR/451は別未完。
