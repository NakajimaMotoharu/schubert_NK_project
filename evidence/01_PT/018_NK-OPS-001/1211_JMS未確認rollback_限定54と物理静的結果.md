# 1211 未確認rollback：限定54と全物理・静的結果

1208/PG-D441/BUG1489/YKT1249。canonical Main/Test **9b80cc9540ff9b23ce45ee0c6893141db407be18**、元74055/PG5800-selected54-v4は01:38:49.509969Z→01:41:11.473879Z、真正0/phase0,0/54件15suite/FES・flaky・rerun・skip0/sourceFixedtrue、六module型/null・SpotBugs0。archive `d324ce456aacc2d7fea9952e21c818081bc348e6945a294afedf4bc63cbedee7`。前v1/PT0・v2/30一failure・v3/54別sourceは分離して保持し、合算しない。

独立5804/元31517実0は全850source・実1665Mainを照合、旧2bbb/1664に対し新一＋既八変更、他1656同byte。旧public descriptorを保持、Web consumerのstatic/owned fatal-signal overload二だけ追加、新型のconstructor以外追加なし。PMD7.28/既patch・Checkstyle14.3/既ruleを維持し、PMD実4/raw1595/処理0、CS実0/指摘0。PMD全体0とはしない。

独立5802実0は元54XML/全15一意method・hash/実行期間・六静的XML/counterと全850source/1665classを読み直して16 design TestIDをjoin、public manifest `1f95938b4d7341efd36333fbbefb40c26c7a2ddd606c64ec959a62e89263d509`。静的public `48fa559a73edeeb7d11fc278fb30d938aa17671e430cb9ede5508ecf43a7c7da`、private proof `3056713dab82cd42ce5242f694ad430d582a8573435eaf91cf7c613c628ce6ec`。通常PTであり拒否代替0。

実counter：新共通型L5/M1/C1/B2、Web ReplyConsumer L37/M4/C1/B8、ReplyConsumers L75/M12/C1/B26は各miss0。ただしAPI helper一branch・各consumerの既startup/close枝等は限定54では未網羅、target七全体100=false。全体/native/CHR/F03/451/trace・正式は未受入。BUG1489/YKT1249とfixture再試験の全体依存は保持する。

## 次の不足補完（着手前）

APIのchecked DLQ-read failure＋rollback正常復帰が、旧fixtureをunknown化した後に別入力で未確認だった。既PT-JMS006/SyncRequestListenerTest.readAndFatalIsolationFailuresRollbackAndRetainPrimaryCauseへ独立の正常rollback fixtureを追加する。SS321§7から原checked例外identity/rollback1/commit0/protocol原因保持を期待し、UNKNOWNのtyped停止と混同しない。JUnit case数増分0、production Main不変更。新test sourceでv5限定54→同Main全850source/1665byteと既静的の再認証（PMD再実行不要）→必要whole3955/587を一回。旧54を新sourceのPASSへ転用しない。
