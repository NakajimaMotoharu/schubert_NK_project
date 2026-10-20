# 1303 API1034実成功・対象実counter、run全体は静的四件で不合格

元exec18617/pg6154-api-factory-close-selected-v2、source **8f0ba4cb06467e5e1c9b25f8360bbc1db4d963ea**。2026-10-20T18:46:02.335507Z～18:54:53.793881Z、531.458374秒、真正1/Maven1/phase[0,1]・入力固定。実 **1034件/175suite、failure/error/skipped/flaky0**（API1029/172＋前guard5/3）、残 **921件/146suite not-run**。予定1955全体を成功へ算入せず、Web/batch/当wholeは未実行。1297/1299/PTPRE039、固定JDK25.0.4/Maven3.9.12/通常自己所有host。

当元API JaCoCoは実測。全対象にmiss0、LINE/METHOD/CLASSは各実コードの正値を確認。適用branch合計232全covered、enum自身のbranchは0でN/A（未測定や0/0を100へ補完していない）。

| 対象class | LINE | METHOD | CLASS | BRANCH |
|---|---:|---:|---:|---:|
| ApiManagementServer |109|13|1|56|
| ApiBrokerContexts |87|16|1|26|
| ArtemisConnectionFactoryProvider |43|5|1|10|
| ConsumerProfile |8|3|1|0:適用なし|
| ApiMessagingRuntime |77|11|1|44|
| QuestionWorkConsumers |63|5|1|24|
| SyncRequestConsumers |87|9|1|48|
| WebLogConsumers |68|8|1|24|

静的はprotocol/storage/bootstrap0、API **CWO_CLOSED_WITHOUT_OPENED四件**（Sync/WebLog/Question/ApiMessagingRuntime.closeのlock呼出位置）。API Main型null/compileは成功したがSpotBugsが未達で、六module静的0ではない。BUG1557/YKT1314を修正前起票し、抑制や既成功の流用をしない。根因未確定を解析器不具合の確定へ読み替えない。

私有PG379/pg6154-api-factory-close-selected-v2/：begin.safe.json **f13490302e0702adb590a35ab2527d91a481d34dfd4cd1f2d710de460a3f975c**、source.tar **42f40dc2b626f1d870a9bc02c8d50801ea50b5cf08bd199fad72b4400ed599f3**、manifest.safe.json **a4fdb91aa532b488f58802039922d2a95bfce5ae06a83d40a7c46ff3836a7f2a**。原XML/API Jar/actual coverage/静的四 finding・元command/環境/時刻/終了を保全、raw秘密を公開0。

1554の旧六oracle補正、1555のfixture警告補正、新provider四＋親一、既全APIは当run内で実成功だが全体認定とは別。6156/6158のgenuine0用資格readerは未発行・このrunを合格化するために条件を緩めない。次は四排他専用lockを411のprivate final monitorへ明示し、同じclose/例外/通知の意味を保って無抑制静的確認、S3bのnative保持PGと関連変更をまとめた必要影響PT・当source全体へ。旧八対象counterを変更後sourceへ輸入しない。正式1964-53/17-190/工数null/QA051final/PTALT未特定代替0/実VM等安全HOLD維持。

追加PG診断PG6159（元77089）actual0：原reject manifest SHA固定、全851Main同byte/元coverage hash、旧caと当API Jarの全compiled class SHAをそれぞれ保存mapへ照合し、既public ABI/五closeのlock→actual child close→closed順序/全closed参照がcloseのみ、provider全12setter/closeの独立RTE/Error範囲、broker state/capacity3/phase取得前準備を確認。公開 `evidence/provisional/PG6159-api-original-jvm-diagnostic-v1/manifest.json` SHA **1b680e08653bd5a5c33f2b456fbb0f038ace9852dc6904b7d1325a618331cfea**。目的はPG_DIAGNOSTIC_ONLY_PARENT_RUN_REJECTED、原run exit1/API静的4は不変、追加build/PT0・六module資格/whole/正式/native/代替PT0。この診断の0を原run合格へ読み替えない。
