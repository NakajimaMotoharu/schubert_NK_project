# Receipt参照 JDBC port単体仕様

NK-WEB-002 / ReceiptReferenceRepository全method/Work interface、FUN001/AUT004/DAT009、UI241/242、SS313/331§9.4/332、QA048/SSC175/329、411/451、765。先に既コードの短TX/close/SQL変換をPGレビューし、必要な当Sourceの全条件PTを行う。Mainは障害修正前起票なしに変更しない。

|Test ID|ReceiptReferencePortTest method・入力・独立期待|
|---|---|
|PT-WEB-RCPTPORT001|literalSqlBindingsAndOwnedOrderMatchThreeColumnLocator。literal select/insert/三bind型/UTC値、READ COMMITTED2、insert close後read、commit後ownedclose、DTO各値のliteral照合|
|PT-WEB-RCPTPORT002|absentRepeatedAndConflictingTuplesNeverBecomeAnUpdateOrAcceptanceProof。empty/同tuple反復/更新件数0と1/異値又は欠落拒否、UPDATEなし・rollback/close|
|PT-WEB-RCPTPORT003|nullAcquisitionsColumnsAndInvalidProjectionFailWithoutNpeOrEscapingResources。nonnull契約のnull拒否、connection/stmt/row/必須DB三列null、invalidid/question/time/別ID/duplicate rowsの固定拒否・close試行|
|PT-WEB-RCPTPORT004|impossibleUpdateCountsAreRejectedBeforeReadAndCommit。-1/2/MIN/MAX件数はread/commitなし、rollbackとclose一回|
|PT-WEB-RCPTPORT005|eachProviderFailureRollsBackAndAttemptsOwnedCloseBeforeCatalogOrIdentityEscapes。connect/setup/prepare/bind/query/next/getter/各close/commit/updateのSQL・RTE・Error、SQLは固定catalog、unknown identity維持、close一回/必要rollback|
|PT-WEB-RCPTPORT006|knownPrimaryAndCleanupPrecedenceMatchIndependentSqlUnknownTable。SQL primary＋各close/rollbackのSQL/unknown/Error、SQL+SQL secondaryに隠れたErrorは同一性保持|
|PT-WEB-RCPTPORT007|originalUnknownKeepsIdentityAndOnlyFixedSecondaryDiagnostics。既Web順位のunknown primaryを同一性保持、secondary SQL/RTE/Errorは新固定診断だけ。SSC329/330のAPI/readiness専用優先を無断に横流しせず、既rcpt005CompoundKnownAndPrimaryUnknownPrecedence独立oracleも照合|
|PT-WEB-RCPTPORT008|concurrentIndependentReadsNeverShareConnectionsStatementsOrResults。own二thread/有限join、別接続・stmt・結果、各commit/close一回、入力値整合|

FixtureはJava JDBC interface Proxy/手作成rows/例外/event recorderだけ、driver/DriverManager/SQL engine/socket/DB/Root/VM/鍵/元dataアクセスなし。null guardのNPE negativeは411 non-null契約拒否、productionのNPEcatch/正常化ではない。実DB TestのBeforeAll/fixtureはコンパイル/実行へ含めず、DB制約/PK並行/実隔離・role/IF025の真正性は未証明のまま。模擬closeは呼出回数/順の検査でありunknown実資源解放を証明しない。

SQL期待はSS331の三column/PK同値/技術locatorだけを独立literal化し、productionmethodからexpectedを生成しない。resultは各propertyの7/時刻/IDを比較し、expectedをSUTfactoryに計算させない。scopeはSessionStoreExceptionの既pure graphだけ、ReviewedProjectionHeldProbeAuditの四heldclassに到達しない静的閉包を765へ固定し、実行後execinfoから全四probehit0も確認する。

予定8method/1class、Main2physical（1abstract interfaceの非実行を報告、除外設定なし）。正常Main PG18642/六SB18648は全input/jarhashで再利用、新Testだけcompile、exactMain/Test PMD/CS・通常jar単exec/session/XML/CRCを独立post。実command/日時/環境/branch/source/終了/coverage/失敗/関連BUG/hashは115結果・manifestへ保存。P01104のDB/実API認可・正式/全451は別、旧exec・failed/notrunをPASSへ加算しない。

着手内PGレビュー判断: 接続setup（auto/readOnly/isolation）で失敗した場合はwork未開始なので追加rollbackを発行せず、owned closeを一回試行して失敗を伝播する。work/commit失敗ではrollback後close、成功commit後closeだけの失敗では再rollbackせず結果非脱出。Mockのrelease成否ではなくclose試行/順を期待する。初回compile/run前の独立oracle補足であり、失敗に合わせた期待値変更ではない。旧rcpt005はunknown primary＋secondary Errorでも原unknown同一性＋固定secondaryというWeb既契約を明示し、API/readinessの別補足と混同しない。

初回製品実行前の境界追加: SQL/unknown同一Throwableをprimary/closeへ再送してself-suppressionしないこと、suppression無効unknownは同一identity/固定secondary保持不可でも正常化しないことを006/007内の追加fixtureで検査する。PG18850 compile0のdraftを保持し、新Test入力hashへ必要なcompile/staticだけ更新する（Mainbuild/旧全体は反復しない）。

## 初回実行後の追加（769）

PG18874/source e8ccb3918は全8成功・F/E/S0だがregisterのstatement.close例外行55/56に2line/2branch未通過が残ったため全Source100/独立post合格へ扱わない。元producer・単exec・XMLは不変保存する。

|Test ID|追加method・独立期待|
|---|---|
|PT-WEB-RCPTPORT009|insertStatementCloseUsesIndependentPrimaryAndSecondarySelectionTable。登録body primaryなし/SQL/RTE/Error×statement.close SQL/RTE/Error。primaryなしはsecondary、SQLprimary＋SQLsecondaryは固定catalog、SQLprimary＋unknownはsecondary同一性、unknownprimaryはその同一性と固定suppressed。全12組でstatement一個、read/commit0、rollback/connectionclose各1、statementclose1を検査。SS331/332と既rcpt005順位から手作成した表。|

当追加も765の同じ普通群。Main不変更、同じJDBC interface fixtureのみ。新9件全class・新単exec/sessionを実行し、元8のexecは合算しない。新compile PG18880、static PG18882、unit予定PG18888。
