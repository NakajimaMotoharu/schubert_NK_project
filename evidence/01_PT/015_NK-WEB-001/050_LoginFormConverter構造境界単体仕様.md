# LoginFormAuthenticationConverter 構造境界 単体仕様

NK-WEB-001/関連NK-AUT-001、主WBS-P007-06、RD FUN001/AUT001..004・UI226/234・SS313§5/314§3・4/342/352、PG-D105。MainD8不変更、constructor/convert/private single全Source。PT_DEFAULT、967/event4001原1/3/6pp cap8。

固定synthetic public username/password/HTTP metadataのJDK HttpServletRequest memory proxyを新作。既SessionFormLoginTestは実provider/session/DB setupを含むため呼出/抽出しない。POST/path/UTF8/type+charset・query内form名（case/percent decode）・null/壊れenum/未知parameter・username/passwordの欠落/多値/null/空、データ取得例外の固定redaction、fatal透過、delegated numeric Caddy peer/header拒否、共有converter2worker8task/10秒joinを独立固定期待値で確認。正常は必ずUsernamePasswordAuthenticationToken未認証/authority空、principal/char[]/numeric addressの値だけ確認しchar[]をzero/eraseCredentialsする。文字列は未正規化入力として保持するconverter責務であり、providerのNFC/パスワード規約/認証成功は確認しない。

実HTTP/transport/network/DNS/認証manager/provider/sessionstore/CSRF/DB/JMS/VM/Root/実key/held4は呼ばない。Caddy resolverは固定numeric literal文字処理だけ、InetAddress/JDKライブラリのmetadata初期化はglobal OS/native0と主張しない。固定SSの拒否message/cause0・期待principalとchar配列・未認証flagがoracle、expected生成にProduction converterを使わない。秘密・実credential/rawsession/tokenは入力/出力へ保存しない。

shared012/profile068、六SDKsha固定、正常D8 JAR compile20112/六SB20114再利用。prepare/static→Git固定→全13単一JaCoCo/全physical1/四counter100/currentCRC/strictpost、アプリ初期化converter/resolver/address/固定例外/新Testだけ、SecurityContextHolder等初期化無しを確認。結果051/manifestに時刻・OS/JDK/tool/command/source/exit/counters/XML/BUG/hashを保存し真正終端後fresh quotaをend_fieldsへ結合。F/E/S/flaky/not-runをPASSにせず全認証/実Caddy/実security chain/CSRF/session/DIF016/451/正式1964-53/工数nullは未受入。

|Test ID|method|
|---|---|
|PT-WEB-FORMPORT001|validDefaultFormRemainsUnauthenticated|
|PT-WEB-FORMPORT002|explicitUtf8AndLiteralCharactersArePreserved|
|PT-WEB-FORMPORT003|methodPathAndEncodingRejectBeforeCredentials|
|PT-WEB-FORMPORT004|missingMalformedAndIncompatibleMediaTypesReject|
|PT-WEB-FORMPORT005|queryFormNamesAndMalformedEscapesReject|
|PT-WEB-FORMPORT006|absentEmptyAndNonFormQueryAreAllowedStructurally|
|PT-WEB-FORMPORT007|nullUnknownAndBrokenParameterNamesReject|
|PT-WEB-FORMPORT008|usernameNullMissingEmptyAndMultiplicityReject|
|PT-WEB-FORMPORT009|passwordNullMissingEmptyAndMultiplicityReject|
|PT-WEB-FORMPORT010|numericProxyRejectionStaysDistinct|
|PT-WEB-FORMPORT011|fixtureFaultsAreRedactedButFatalIsNotHidden|
|PT-WEB-FORMPORT012|nullApiBoundariesReject|
|PT-WEB-FORMPORT013|sharedConverterKeepsParallelInputsSeparate|
