# PG6262 JDBC返却前setup横展開仕様結果

BUG1567/YKT1324・SSC320、RD MQ/ASY・UI213241/SS324332354。source97dd2ba6185143632439f32dfc1d663061f1e55c。PG6262は当sourceの原113 snapshot/851Main/1667class資格PG6248（4495f377）を入力にした**source/JVM静的読取だけ**。Java program、JDBC、SQL、PT、VM、サービス起動0。全19owner/21setAutoCommit(false)を出典hash付きで照合、真正0。

公開 `evidence/provisional/PG6262-jdbc-setup-scope-v1/manifest.json` SHA256 `efea67efd80f9e4da899a28a279345ffc2cab41ad00412561d98c5207011f947`。ownerごとのpath/source hash/Jar hash/method/false定数/実BCI/保護exception table/実close又は明示helperを記録。動的成功・coverage・全複合例外の安全性へ拡大しない。

| 構造 | 対象/箇所 | 当原因への根拠 |
|---|---|---|
| TWR内のsetup | UserMutationApplicationService/UserQueryApplicationService/LogQueryApplicationService/MediaApplicationService/QuestionMutationApplicationService/QuestionQueryApplicationService/QuestionSubmissionService（3scope）/QuestionWorkerService/ScenarioApplicationService/JdbcSyncRequestProcessor/WebLogIngestService/InboxCleanup/WebRequestLogProducer/EncryptedWebSessionRepository、14owner・16箇所 | connectionはsetAutoCommit前にTWRへ登録。原JVMにsetupを包含するThrowable/Error/finally保護とcloseあり。別種の同一Throwable/TWR複合順位の全安全性は本確認から断定しない |
| 明示全体try/finally | WebLogDispatcher 1/ReceiptReferenceRepository 1 | setupのErrorも保護。前者は同一methodのcloseAfterFailure port→一つのactual Connection.close、後者はfinally direct close。borrowed/raw connectionの流出なし |
| 失敗状態を捕捉してからclose | RevocationRetryCoordinator 1 | SQL/RTE/Errorをfailureへ保持し、非null connectionのrollback/closeとpreserveFatal後に結果判断。捕捉しただけで成功へ戻さない |
| 借用接続 | BootstrapAdminMain.createAndCommit 1 | method内open/getConnectionなし、callerが所有する接続の設定を行う契約。新たなowned factory返却前close漏れではない。ADMIN/Rootを実行したという意味ではない |
| 当該 | OutboxDispatcher.transaction 1 | setupをSQL/RTEだけで保護、callerへ未返却かつError保護/closeなし。BUG1567の直接対象、まだ未修正/未動的再現 |

対象外はbatch/実Root/失敗cohortの新実調査・回収・操作。既当原因と無関係なborrowed/正常callbackへのclose追加や、全TWRを機械置換しない。検索だけ完了にはせず、直接対象は独立Error setup・close matrix/副作用counter・修正/再試験/同source必要回帰が揃うまでOPEN。非該当側は上表の個別構造と当原classを根拠とし、正常既wholeへの同source対応は別途原6250で確認する。

新工具初期定義で未使用Path importのpyflakes1、WebLogDispatcherがdirect closeでなくprivate helperである点を未対応にしてguard終了1（詳細化後も同対象終了1）を保全事項として記録。いずれもPT/JDBCを実行せず、Production不具合へ読み替えない。完成定義ではhelperを実名・一actual closeへ限定し、guardを削除/任意close許可せず全21へ適用、最終pyflakes0/事実読取0。静的検査をPASS件数やPT代替へ加算0。

次=進行中元6244/1795の真正終端→原6250回収→当source trace/静的case join、保存後のみSS320新独立proxy再現/二Main PG・必要PT。6258既943更新/6260個別case joinはpyflakes/定義だけ準備、当4034真正原資格前に実行しない。元sourceはfreezeを維持する。

正式1964/53・17/190・工数null・QA051final・PTALT対象不明代替0/実VM等HOLD不変更。通常静的結果/commitで停止しない。
