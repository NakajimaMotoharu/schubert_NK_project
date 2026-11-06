# AuthSessionRevocationService：Logout・管理失効の自己所有境界単体仕様

NK-AUT-001/WBS-P007-05（owned3 artifactの当1source、全leafではない）、AUT001..004/MON004・UI226/234/SS312§4.2/314§6.3/332/352§12・QA050 clock fence。対象constructor/logout/logoutCurrent/revokeAll/arguments/requireTransaction/update、全source/physical1。元seed未登録/PG20458 strict pin無し、元実DB試験は未抽出/未再演。自己所有Connection/Statement/ResultSet/Clockだけ、Source名のLogout/ADMINはfake JDBCへのmethod-level stageであり、実request/DB/session/権限を操作しない。PUBLIC64ASCIIa/hash・fixed synthetic UUID/UTC rowだけ、鍵/AES/本番credential/DB dump不要。

|Test ID|method|入力・独立期待値|
|---|---|---|
|PT-AUT-REV001|logoutSamplesCurrentClockAfterBothLocksAndStagesExactUtcAudit|User→Session lock query/row.next後だけclock.instant一回、micro UTC/LOGOUT update/0000 critical audit、Hash bindとidentity固定。legacy Instant wrapper/数値IPだけも確認、caller commit/rollback/close/config変更0|
|PT-AUT-REV002|alreadyRevokedReturnsOriginalInstantWithoutTouchOrPrincipal|revoked=trueなら元revoked_at/0200、update0・LOGOUT監査一回、status/expiryを再認証grantへ読まず返却DTOはredacted、active principalを作らない|
|PT-AUT-REV003|expiryDisabledAbsentAndNullRowsFailClosedWithRequiredAuditOnly|expiry同時刻/1micro前はEXPIRED update+0102 auditをstageして認証拒否、1micro後は成功。disabled/不在は不要なupdate/audit0、必須六column nullは固定Infrastructure、clockはlock後だけ|
|PT-AUT-REV004|administrativeRevocationStagesEachTargetInFixedOrderForAllowedReasons|現在DB認証済みADMINを模したactor9/target7、DISABLED/PASSWORD_RESET/ADMIN各理由・対象session0/1/2、ID順select→各ID update+actor9/target7監査、件数・全UTC/SQL/bind。target1/N12最大、actual ADMIN request無し|
|PT-AUT-REV005|boundaryNullOwnerReasonAndCurrentAdminContractsPrecedeSql|constructor/三APIの全参照null、N12 -1/0/最大+1、非管理失効理由三種、USER roleをSQL前拒否、transaction前提違反は固定Infra。requireNonNull契約拒否を成功化せず、正常ケースの不意NPEとは区別|
|PT-AUT-REV006|affectedSqlAndEveryCloseFailureRemainUnsuccessfulAndRedacted|update/audit affected0/2、Logout/管理双方の全prepare/query-update・全取得close、context/NotFound primary+SQL closeは固定Infra、通常NotFoundは非漏洩0104。既取得一回close、provider marker/cause/suppressedを固定化|
|PT-AUT-REV007|invalidValuesAndUnknownProviderExceptionsKeepTheirDefinedBoundary|不正owner projection/極端Clock時刻/管理session ID null、未知IllegalState同一性・Logoutの既定IAE分類、全driver getter/setter/next・null-address bind故障、失敗を成功へ戻さない|
|PT-AUT-REV008|sharedServiceParallelCallsRetainOwnResultCorrelationAndResourceState|同じService/ContextHashを二worker16callbackで共有し、各独立row/Clock/Connection・revoked混在・message/correlation固有。返却時刻/resultと各監査correlation・Hash bindを独立確認、全Future終了。実DB lock競合の再現とはしない|

SQL/順/UTC/ResultCode/critical audit JSONはSS314/332/352から手書き固定し、Productionのprivate定数/処理結果からexpectedを生成しない。公開Hash vectorは既独立Python算出済み値を使用、NULL inetはJDBC setNull Types.VARCHARを明示検証。時刻は固定micro literal、Clock自身がUser/Session query・row.next後かつsession row未closeをassertし、直前の早いsampleと区別する。Optional clientは空またはInetAddress.getByAddress固定IPv4だけ、DNS/connect無し。普通SQLException/Runtimeだけを使用し、cycle/graph/fatal入力を新規実行しない。SessionAuditWriter/AuthorizationService/ContextHash/DTOは必要な純粋依存として通るが別sourceのcoverageに混算しない。

Java25.0.4/JUnit1.13.4/JaCoCo0.8.15、normal20704/sourcefb189、全1844Java/POM/class同byteと確認した静的20114 D8だけ参照。profile093 prepare/static→source commit/push→単一8Unit→元producer/config/SDK static/source/CP/init/XMLをGit固定→strictと独立post。全physical1四countermiss0・全@Test FESaborted0・CRC normal同一・単一exec/session、合成/手動除外/意味のないassertion無し。JDK SQLException getter初期化の既静的20846は同modules/javapだけ再利用、当source/fixture/Gson/環境を別照合し、SDK metadata/OS syscall0とはしない。VM/Root/DB/keys/held4/QA055/native/CHR/全451・QA051 finalのHOLDは維持。

元見積1.5/4/7cap10/event4061・主P00705、S/V別。元WBSの限定監査費予測を当whole source oracle補完の群見積へ書換えず、再認証/発見/手戻り・費用を分離し、未測定専有費/N/T/工数率はnull。全3sourceのInbox/replay/実DB競合/権限/実経路条件が未完のため当1sourceだけでleafを閉じない。結果048へsource/run/branch/時刻OS/JDK/command終了code/coverage/BUG/証拠hashを保存。

BUG2363/YKT2108の元20932 compile0/20934 PMD10・CS6/Unit未実行を保全し、column/action四定数と六複数宣言を修正。現20936 compile0/20938 raw6・各用途非該当6/適用0/CS0/処理0、抑制無し。元8method/物理1/見積不変。呼出元LogoutInboxService103～120は実clockをlogoutCurrentへ渡していると読取確認（実経路受入ではない）。既終了compile sessionへの余分なread-only pollはUnknown processで終了し、既manifest0と区別、compile/Unit再起動無し。

BUG2364/YKT2109：元PG20940/source7caa341はF1/E1で不合格、counter100でも資格加算0。UI234正本8deb209のline68は既失効0200、SS351 code表/SS354line297も0200、0001は閉じた表に無い。fixtureの根拠未照合が原因でProduct/上位資料は正しい。元source/config/driver/XML/exec/coverage全保全後、期待literal二箇所と本PT仕様を0200へ訂正。新metadata oracle016は正本Git/doc hash/行/code集合を固定し、profile093のprepare/run/post前にfixture literalを検査する。0001→0200は実際値への追従でなく承認済み正本による是正。新source全8を必要再試験し、元6成功を算術流用しない。原1.5/4/7cap10とTestID8/物理1は維持。
