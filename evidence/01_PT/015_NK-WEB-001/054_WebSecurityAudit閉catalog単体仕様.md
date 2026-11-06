# WebSecurityAudit closed catalog 単体仕様

NK-WEB-001/WBS-P006-04、AUT001..004/MON004・UI226252・SS314/351§3/4/6・352、PG-D107。正本origin/main8debで351SSC046のretry0..900秒を確認、勝手に1以上へ変更しない。MainD8と元503のSource SHA ce6fc0f8が完全同一、元CLASS2covered+1miss=3/現normal3（main/Event/Route）。元4表記はBUG2332/YKT2077へ先行起票し4009/975で訂正、原counter/元event4007は保持する。

PT_DEFAULT、974/event4008原1/4/8pp cap10。実backendのないSystem.Logger実装が自己所有queueへ固定fixture JSONを保持するだけ、System.getLogger/実ログ出力/DB/HTTP/securitycontext/sessionstore/鍵/Root/VM/held4は呼ばない。固定ClockのISO UTCミリ秒、閉10Event/5Routeのaction/reason/outcome/level、nullable actor/IPとLOGIN/LOGOUT制約、retry0/1/900及び-1/901、version1/64と0/65/不正、canonical numeric IP/45文字境界/zone拒否、null/Clock・sink故障/fatal透過、NFC/Unicode line-separator redaction、2worker8record・10秒joinを全10methodで確認する。actorのCR/LF/TABはSessionPrincipal invariantが先に拒否するためreflectionで破らず、許容U2028/U2029のsanitizeを実測する。

独立oracleはSS351 catalog固定表/JSON key集合/日時literal/IPv4・IPv6固定vector/例外固定文。Production logger/record/formatterでexpectedを作らない。JSON parserは受領値の解析だけ、context/cookie/token/password/body等は許容key集合へ入らないことを確認。fixtureはpublic principal/doc IPs/dummy contextだけ、実秘密は無し。出力は要約とhash・coverageのみ、raw実ログ/credentialは保存しない。Local JSONの単体でありAPI critical audit/永続化/outbox/実handler/CHR/nativeを合格としない。

shared012/profile072、Gson2.14.0/annotation2.50.0 exactsha。prepare/static→Git固定→全10単一exec/全physical3/四counter100/CRC/strictpost、既normal20112/SB20114成功確認再演0、元partialとのcoverage union0。enum compiler default filtersはengine標準だけ/手動除外0。結果055/manifestへ環境/command/source/exit/XML/counters/BUG/hashを結合、末尾freshは真正終端後に取得。正式1964/53・歴史17/190・工数null/全451未受入。

|Test ID|method|
|---|---|
|PT-WEB-SECAUD001|allTenEventsMatchIndependentCatalogAndJsonSchema|
|PT-WEB-SECAUD002|allFiveRegisteredRoutesAndOptionalFieldsRemainClosed|
|PT-WEB-SECAUD003|actorSeparatorsAreRedactedAndContextNeverAppears|
|PT-WEB-SECAUD004|lockRetryBoundariesZeroOneAndNineHundredAreExplicit|
|PT-WEB-SECAUD005|invalidMetadataNeverEmitsARecord|
|PT-WEB-SECAUD006|nullConstructorAndRecordContractsReject|
|PT-WEB-SECAUD007|literalAddressesCanonicalizeWithoutDnsAndInvalidInputsDoNotLog|
|PT-WEB-SECAUD008|versionOneAndSixtyFourAreRetainedAndInvalidFormatsReject|
|PT-WEB-SECAUD009|clockAndLoggerFailuresPropagateWithoutProviderDiagnostics|
|PT-WEB-SECAUD010|concurrentRecordsKeepRequestIdsAndActorsSeparate|

BUG2333/YKT2078: initial072のhelper命名1をexpected不変で是正、最新073でcompile/staticを取り直し、全10は最新sourceだけを一回実行する。原static20430のraw3は保持。

## Test IDとmethodの明示結合

上記固定oracle・正常/境界/例外の目的を当sourceの選択全methodへ一意に対応付ける。番号はTest sourceの宣言順であり、追加PTや再実行を意味しない。

|Test ID|class.method|
|---|---|
|PT-WEB-AUDITPORT001|WebSecurityAuditPortTest.allTenEventsMatchIndependentCatalogAndJsonSchema|
|PT-WEB-AUDITPORT002|WebSecurityAuditPortTest.allFiveRegisteredRoutesAndOptionalFieldsRemainClosed|
|PT-WEB-AUDITPORT003|WebSecurityAuditPortTest.actorSeparatorsAreRedactedAndContextNeverAppears|
|PT-WEB-AUDITPORT004|WebSecurityAuditPortTest.lockRetryBoundariesZeroOneAndNineHundredAreExplicit|
|PT-WEB-AUDITPORT005|WebSecurityAuditPortTest.invalidMetadataNeverEmitsARecord|
|PT-WEB-AUDITPORT006|WebSecurityAuditPortTest.nullConstructorAndRecordContractsReject|
|PT-WEB-AUDITPORT007|WebSecurityAuditPortTest.literalAddressesCanonicalizeWithoutDnsAndInvalidInputsDoNotLog|
|PT-WEB-AUDITPORT008|WebSecurityAuditPortTest.versionOneAndSixtyFourAreRetainedAndInvalidFormatsReject|
|PT-WEB-AUDITPORT009|WebSecurityAuditPortTest.clockAndLoggerFailuresPropagateWithoutProviderDiagnostics|
|PT-WEB-AUDITPORT010|WebSecurityAuditPortTest.concurrentRecordsKeepRequestIdsAndActorsSeparate|
