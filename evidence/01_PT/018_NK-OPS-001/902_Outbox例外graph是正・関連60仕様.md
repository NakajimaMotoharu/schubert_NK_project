# PT-OPS-CAUSE3404-001～003 是正・関連60仕様

BUG1299/YKT1065、WBS-P006-02、RD MQ006/008/AUT001～004、UI242/226、SS314/324§8/331/352/355/411/451。独立before899/901で三非終了と一型見落としを実証済み。現配備a9/PG2802は保持し、修正は未配備候補と区別する。

API OutboxJmsSenderはidentity訪問済みqueueでcauseとJMS linkedの両edgeを有限走査する。非null入力はconstructor/内部契約どおり明示拒否、直接self/複数nodecycle/DAGを同じ型の有限graphとして扱う。typed ActiveMQDuplicateIdExceptionのみtrue、message/suppressed二次rollbackだけはfalse。Web依存やJMSを含む新common moduleを追加しない。業務正本/承認DIF変更なし、内部分類5の是正、追加QA不要。

| ID・Test method | fixture・入力・操作 | 独立期待値 |
|---|---|---|
| 001/cause3404TypedGraphTerminatesCyclesAndVisitsBothProviderEdges | 標準cause二node・JMS混合cycle・別cause duplicate・共有DAG・suppressed/messageのみ・equals/hash呼出し禁止型・null | finite false/trueはfixture実型とedgeからliteral判定。値equals/hashを呼ばない、nullは境界NPE拒否（catch正常化なし） |
| 001/cause3404UnconfirmedCommitAlwaysRollsBackClosesAndPreservesOriginalGraph | 独立SS323固定offset wire/sample、公開send、commit例外cycle二種、rollbackに二次duplicate、close障害 | OutboxSendException固定message、causeは同一原例外、原suppressed=[rollback]、wrapper suppressed=[close]、順序commit→rollback→close各一、二次duplicateを確定成功にしない |
| 001/cause3404ReachableTypedDuplicateConfirmsOnlyAfterRollbackAndStillCloses | 原commit cause/linkedcycle＋到達可能なtyped duplicate、正常rollback/close | send正常帰還、commit→rollback→close各一、原suppressed0 |
| 002/AuthenticationFailureGraphTest | suppressed二nodecycle・後からreachable AssertionError | 元graphは有限帰還、typed fatalは同一objectでthrow、redactedcatalogへgraph格納0 |
| 003/SessionFailureGraphTest | cause/suppressed混合cycle・後からreachable AssertionError | 元graph有限、typed fatal同一objectでthrow |

Test timeout10秒は回帰の非終了検出でありtimeout自体は合格にしない。Proxyは公開JMS interfaceの故障fixtureでありprivate reflectionなし。wire fixtureは既独立SS323 offset（320byte、header256/data64、26/12/12/14）を保持し、Production encodeでexpected生成しない。新三API method以外の旧16と、Web typedcycle既5/RetryCoordinator既8、全既再送/DB/Broker所有試験も関連scopeで実行する。

関連PG3408はnew-only source/archive固定、Java25.0.4/Maven3.9.12/Node24.19/PG18固定root、六module compile/NullAway/Spotless/SpotBugs。対象はProtocol7/1suite、Storage8/1、Bootstrap5/1、API20/2、Web14/3、Batch6/3、合計**60/11/1643Main**。元3398 Main memberと比較し変更はAPI OutboxJmsSender.class一件だけ、他1642Mainと全resource/debug memberは同byteを要求。変更methodのLINE/METHOD/BRANCH全missed0を照合。旧a9 nativeを候補へ合算しない。command=`PYTHONPATH=tools/quality python3 -B tools/quality/pg3408_outbox_cause_related.py`（clean commit後一回）。元exit/XML/log/input/coverage/hashはprivate pg3408-outbox-cause-related-v1/remotePG3408-related-v1へ格納、結果を別記する。

YKT対象は全MainのgetCause/getLinkedException/getNextException/getSuppressed呼出しを網羅検索。graph走査はAPI対象・WebLog・RetryCoordinator・SessionStoreException・AuthenticationInfrastructureException、他は一段取得/固定suppressed長判定で再帰/loop追跡なしとし一覧・source hashと再発防止を保存する。非該当を検索だけで完了にせず、上記既/新Testの実source・XML・cycle/fatal identity後条件を結ぶ。

新candidateは関連60後に必要全3712/545の真正結果・独立source/run/全member・当source nativeへ進む。既a9/全3707/native28の成功を新candidateの全体合格へ流用しない。正式1964/53、個別17/190、工数null、QA051final保留、F03/PMD2220/Checkstyle645は据置き。
