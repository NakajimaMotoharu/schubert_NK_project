# 1223 commit済terminalの入場停止：単体テスト仕様書

NK-MSG-001/NK-WEB-002、RD MQ008/010・UI231・SS321§7/322§11/352、PG-D444/BUG1501/YKT1261。隔離commit後exitは、同じreceiver groupの後続callbackを入場停止する独立期待である。readyfalse/通知一回だけを成功条件にせず、後続のmetadata/DLQ再送/commit/業務/rollbackも停止する。修正前Mainはsource862、全851/1666・既private/public proofを保持する。

| Test ID | class/method | fixture | SSからの固定期待 |
|---|---|---|---|
| PT-JMS-TERM001 | api.messaging.inbound.CommittedTerminalAdmissionContractTest.term001SyncCommitStopsAllFourContextAdmissions | Sync四context、wrong JMS type、隔離read/send/commitは正常 | 最初metadata/send/commit各一、protocol通知一/fatal0/business0・readyfalse、その後全四contextへcallbackを再度渡しても全値不変 |
| PT-JMS-TERM002 | 同.term002QuestionCommitStopsFurtherAdmissions | Question一context、同上 | 最初一回だけ、次callbackに入らない |
| PT-JMS-TERM003 | 同.term003WebLogCommitStopsFurtherAdmissions | WebLog一context、同上 | 同上 |
| PT-JMS-TERM004 | web.messaging.ReplyCommittedTerminalAdmissionContractTest.term004ReplyCommitStopsFurtherAdmissions | Web reply一context、同上 | 同上、terminalFailureObserved=true |

メモリJMSContext/JMSConsumer/JMSProducer/Message proxy、固定Clock、限定portだけを使用。plain MessageはBytesMessageではないため恒久不正とし、DLQ metadataはnull/default許容値、producerは同期staging成功、commit正常を合成する。first段階でprotocol1/fatal0/send1/commit1を先にassertし、別のError停止を誤ってPASSにしない。未知methodはcounter＋AssertionErrorで拒否し未知call0をassert、callback内close0・owner closeが全context数であることも確認する。期待値はproductionから算出せずSS322と明示0/1から定める。

API helperは既FatalIsolationFixtureのAPI内拡張で、元ISO001～006の失敗modeは不変更。Webは独立fixture、存在しないAPI test-jarに依存せずPOM追加0。実Broker/DB/VM/Unit/実session/原本/鍵/permit/failed-cohortを操作しない。拒否境界の試行やPT代替ではなく通常PT。

まずtest-only sourceで`pg5854_committed_terminal_red.py red-api`（予定11/7、API三目的failure時Web一not-runを保持）→未実施Webだけ`red-web`（九/七）を実行する。元Main全851source/1666実classが862と同じことを独立照合。API Syncのpost値は修正前5、他API/Webは2になり、metadata/send/commitの三assertだけがexpected1に反することを確認する。初回段階・未知call・型/null等の別失敗があれば目的redにしない。NoTests/strict warning/formatを維持、skip/error/flaky/rerunは合格0、empty targetをcoverage100にしない。

red後のPGでは四consumerのCommittedFatal catchにhalted=trueを加え、最初のcommit/ACK・通知一回を維持する。普通のrollback再送、非commit isolation/unknown/Error、既inflight/他groupのowner責務は変えない。旧API統合TestのprotocolFirstだけをbusiness/questionCalls/rollback0・commit三（各group一）へSSから訂正し、元brokerの正常後続wireが未処理/未ACKでowner close後に戻る独立後条件を確認する。元protocolFirstの仕様違反を許すPASSは改記せず履歴として保持。

当redはAPI元69479/10case六suite・目的三failure、Web元82962/九case七suite・目的一failureだけ、全851/1666は元862同byteで成立。5855独立元XML検証実0/公開e4419d0226f86570831110cb62bc7663b7675d5acc8582f134a1e30e186d9d5e、redを成功PTへ加点0。greenは`pg5856_terminal_green.py`（旧66＋新四/計70・20suite、target八/実1666）で実行し、同じ@Test内でpost-terminal後のSync四contextを各一workerから同時callbackしてvisibilityも確認する。これはgreenで追加実行する並行観点であり、初回redで実行済みとはしない。Questionの実返却は既独立QWKREQ01の全byteを比較、元TTL/遅延は不変更・既10秒待機で確認する。最終は`pg5858_terminal_static.py`の全851/1666・四catch一行以外不変更/ABI/無除外staticと必要same-source全体へ進む。

green-v1/元69878はsource1e55289a1、format0の後WebLog変数result誤記でcompile1。13/5のみ・API/Web/batch未実行であり70成功ではない。BUG1502/YKT1262を起票後runtimeへ是正、静的期待表も元factory宣言と照合するunitへ強化した。元archive caf1760656e385aab65e955bbaffb252ff9bb75de19ba3bb57a8515f82f09edeを保持し、新sourceのv2だけを実行する。単一JMS contextへの不正な再入fixtureで枝を人工到達させず、未網羅は実測値として残す。

次のgreen/静的/必要全体は新sourceを固定して仕様・command・対象commit・環境・全counter/XML/hash・関連BUGへ追記する。旧6b5-3967/862-protocol105/旧nativeを新sourceへ合算せず、正式1964/53・17/190/工数null・QA051final/実所有HOLDは維持。現在は四red成立・是正PGの受入待ちでありPG/PT完了ではない。
