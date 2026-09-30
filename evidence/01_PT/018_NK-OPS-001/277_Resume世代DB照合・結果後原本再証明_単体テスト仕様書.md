# NK-OPS-001 Resume世代DB照合／結果後原本再証明 PT

関連: OPS009/BAK001/BKO001/UI251、SS341/343/331、SSC114、BUG347/348/YKT277/278。Class/method: BackupWorkerRequestFiles.prepareResumeReplacement、MorningBackupRequestPublication native resume proof、MorningBackupStage.verifiedEpoch、MorningDatabaseSession.Access/Session.requireAbandonedRequest/recheckConsistent、MorningProcessMain retirement callback。

BREQFILE010: 旧literal NKBACKUP1の同run/旧実開始時刻と新実時刻を別fixtureで作る。proofがDB不明を投げる場合は旧byte/新part不存在を確認。proof呼出時は旧byteがまだ存在、成功後だけ旧retire→new-only公開し新literal byteを比較。異run/時計逆転はproof0、同byteは厳密再読で変更0、MISSINGのみ新公開、null全境界拒否。前後metadata/namespace、全所有close・rawbyte消去は既存BREQFILE suiteと回帰。callback自体はmockでありnative DB根拠の代用ではない。

MDB016: 独立PostgreSQL18/Flyway023 fixture、実専用batch session/advisory。初回両RUNNING commit、session close、同run/cutoff resumeの新実時刻beginにより旧両ABANDONED/新両RUNNING、attempt各2を確認。古い公開requestの実開始時刻に対応するexact2 DB rowのstatus/reason/attempt/ended/business_dateを新read-only transactionで読取り。foreign/新時刻/null/完了後/closed lifetime拒否。post-begin専用recheckはbefore-begin拒否、begin後・実両FAILED commit/readback後に同原本参照一致を再確認する。旧pre requireConsistentのbegin後拒否は維持。期待SQL string_aggは固定literal4行のstep/attempt/status/error_code、Production methodでexpectedを生成しない。

RunReferenceRepositoryはRW-configured/autoCommit=false borrowed connection契約のため、post proofはJDBC readonly flagを偽らず `SET TRANSACTION READ ONLY` によるserver read-only transactionで読取→rollback→autoCommit復元する。既存schema/advisory/owner thread/lifetimeは維持。最初の新MDB016失敗（selected.logの新port transaction未完成）はTDD未実装扱い、合格不算入。修正後selected2: Bootstrap9+Batch59=68PT F/E/S0/static各0、2026-09-30 11:40:59 JST、JDK25.0.4/Maven3.9.12/固定offline m2、同Bootstrap+Batch reactor `spotless:apply clean test spotbugs:check`。対象sourceは本仕様と同commit固定する。未網羅/全scope正式認定/native結果は別gate。

前のPG384 full6 sourceba126a25b: 2540PT/371suite F/E/S0/static0、11:22:01/13:06、manifest75deec63…。未網羅B/L/M/C269/1094/251/23。実署名/RO全BOM・新INVALID/Rootapproval/current切替成功だが、外部Morning Invocationbfa3d9e4d4d4408f948d4198e431276eは旧request/new content-start不一致でworker開始0/exit30。manifest4b80d2e9…とsame-byte parent.exec保存、旧失敗を新成功へ改変しない。DB旧2ABANDONED＋新2RUNNING、request原本87byte・run/cutoff不変、marker0/permit0。

次のnative終了条件: 実新候補を署名/RO BOMで検証して新INVALID・旧Root材料保全・current再読→外部同run resumeで旧request/DB照合・新公開→真正Backup fresh Invocation/全Unit終端→実dump/pg_restore/config/age/MANIFEST→同owner両SUCCESS/独立SQL再読→原本/current/参照確認→request/marker退役。known FAILED/timeout/UNKNOWN/残留隔離・全4coverage100%・S2/issuer/APIWeb/CHRは別必須、まだNOT-RUN。未実行をFAILED/SKIPPEDで埋めない。
