# 683 NK-BAT-001 Morning成功Backup行projection（限定PT）

## 最終sourceの追加fault・再資格（2026-10-13 02:06JST）

MDB-PROJ-1737-007（method mdbProj1737007AllowedJdbcFailuresAndUnknownProviderIdentityCloseEveryResource）：JDBCが許すSQLException及び未知RuntimeException/Errorをquery/read/closeの六地点へ独立注入。SQL例外は固定IOException/redaction/cause無し・suppressed0、未知二種は元object identityを保持、connection/statement/rows全0・commit0を各確認する。.03:deliverable/qualityのJDBC例外・close・資源後条件に対応するが、実OS/DB lock所有の認定ではない。

新Test source89a8ad0ac31e54038d5d598ead97d39c95f30a93、formatter1.36.1後にPG1739 exact7/FES-aborted-notrun0/Werror0/全MainCRC0、serverSHA535cf158e7955a50152c5d871f18deb9cdefb1de1038b170f8279d0d2bac8efd。別PG1740 exact unique7/source/library/JAR/fixture/exec/XML独立資格0、serverSHAa346f4429117583c9a9550e5c5a3c919259c2f276681c317a0b57fbb2e0eb27a。sourceが異なる初回6を最終source7へ加算せず、7だけを当限定合格とする。Main/VM/元fixture不変、faultを加えた追加counter改善0だが例外/close契約の反例証拠が増えた。残870/169/9/705は同値、fresh全3604は未実行、正式/子03 NOT_ACCEPTEDを維持。開始見積り0.5/1/3は不変、結果event0509、N/T・子別実費null。下記初回6は履歴。

Program/class/method：MorningDatabaseSession.Session.successfulBackup/successfulHandle、ProbeはTest専用provider。関連OPS009/DAT009／UI251／SS331332343354、主leaf **WBS-P017-01.03**（原本/JDBC/lock例外・close・資源後条件）。初回event0507は親P017-01だけを記録したため、0508で子へのTestID/criteria対応を追記訂正。開始0.5/1/3pp・原見積り/v3を上書きせず、未分離個別実費はnull、親子/参照費を重複加算0。

独立fixture：SQL resultの2行をliteral Mapに定義。run31100000…／cutoff2026-09-27T15:00:00Z、business_date2026-09-28（Asia/Tokyo）、id1737001/1737002、DB target/success1、config2、failure0、byte26/67、start02:00:00Z/end02:00:03Z、attempt1、error2列null。正常Expectedは固定id・step・start/attempt値を直接assertし、Production methodでExpected生成0。Scope/ROLE/lockのproviderは合成fixtureであり、実host runlock/DB所有権を与えない。共有Main JAR6と既fixture byteを前後pinし、専用classes/XML/exec/portなしのLAN実行を隔離する。

| Test ID（method末尾） | 入力・操作／独立期待値 | 子criteria／実結果 |
|---|---|---|
| MDB-PROJ-1737-001 BothSqlOrdersReturnLiteralIdsAndNoMutation | DB/config両順を供給、戻りid・step・attempt・start固定値、connection/statement/result全0、commit0 | 正常control（.01所有取得の受入ではない）、PASS |
| MDB-PROJ-1737-002 EmptyMeansNoReusablePairAndIncompleteOrExtraRowsReject | 空はOptional.empty、片方/第三行/同step2行はIOException、全資源0、commit/rollback業務変異0 | .03:deliverableの欠落/余剰/形拒否と資源後条件、PASS |
| MDB-PROJ-1737-003 EveryRequiredProjectionNullRejectsWithoutNpeOrLeak | step/date/start/end/target/success/failure/byte/id/attempt各列・両行をnullにする、IOException（NPEは合格にしない）・全資源0 | .03:qualityのDB result null契約/negative/close、PASS |
| MDB-PROJ-1737-004 EachSemanticFieldCounterexampleRejects | 異business_date/end<start/target3/success0/failure1/byte0/error非null/CLEAN_LOG、両行の単独反例。end>観測、非microsecondも拒否 | .03:deliverableの各不整合IOExceptionと原値・資源0、PASS |
| MDB-PROJ-1737-005 PairAttemptStartAndEndMustBeOneBundle | configだけattempt/start/endを別値、独立した二成功をbundleへ認定しない、IOException・全資源0 | .03:deliverableのpair不整合/close、PASS |
| MDB-PROJ-1737-006 EndAtObservationAndPositiveByteBoundaryRemainEligible | end==観測03:00Z・byte1が両行で正常、固定DBid・全資源0 | 境界control（.01/.02受入ではない）、PASS |

実行：SourceTest95920a849083ab85a42eaa31b028e504e6653be0、Main2741c4546afad6c1e8b6efbd53dfb58144edf7bb/JAR変更0。`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<fixed pyflakes> python3 -B tools/quality/pg1737_successful_backup_projection_selected.py`。専用LAN JDK25.0.4/Jupiter5.13.4/Platform1.13.4/JaCoCo0.8.15、GoogleJavaFormat1.36.1整形後にfixedsourceで実施。actual0/exact6/F-E-S-aborted-notrun0/JavaWerror0/全MainCRC0/元fixture不変。server manifestSHAaf9769f6159dc8d8e523ebf3f4535b2186b37280558196165f28f43db7ba69e3、scriptd483779b…。

別read-only `pg1738_successful_projection_qualification.py` は6 unique TestID・XML・全source/library/JAR/fixture/exec/coverageXML値を照合してactual0、serverSHA11b07c567f86d1a3a7126502dcc6d6fd02d863360a1c1875f9571c97a18df660。試験再実行0。個々のloops/assertionをPT件数へ換算せず新Test6だけ。実DB/VM/Unit/原本/Backup変更0、DB fixture起動0（旧TestのBeforeAllは選定しない）。障害発見なし、Expected literal修正/Production変更なし。

当同Main6host＋current9native＋資格済API5＋新6の残870line/169method/9class/705branch、直前873/169/9/715から3line/10branch減、四100false。新Test6追加後、fresh全3603は未実行（先の3597も未実行）。formal1964PT/53scope/wholeleafdelta0を維持する。

終了依存：.03は.02の再入/失効/同時owner matrix及び全原本/JDBC/lock例外・closeを要し、今回6はその一部分だけ。.01実正常owner取得/解放、.02、親scope/全criteria/trace/451を本試験で認定しない。Nのnative実所有・K01全回帰・G13をこの費用へ加算しない。私有証跡：WorkPG379/pg1737-successful-backup-projection-selected-v1/pg1738-successful-projection-qualified-v1、LAN runs/PG1737-selected-v1/PG1738-selected-qualification-v1。公開対象はsafe source/hash/counterのみ、rawcredential/session/cookie/token/DB実体0。状態=当projection6限定成功・子03 NOT_ACCEPTED。
