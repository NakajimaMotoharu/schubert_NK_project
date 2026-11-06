# EncryptedSessionCsrfTokenRepository 自己所有Servlet単体仕様

Program NK-WEB-001、EncryptedSessionCsrfTokenRepository constructor/generateToken/loadToken/saveToken/materialize、RD FUN001/AUT001～004/UI226/SS314§7.2.1/8.1・352。主owner/cost WBS-P015-02。開始4074原1/3/5pp cap8。whole一Main、physical1予定。既seedNOT_IN_CURRENT_MEASUREMENT_REGISTRY/strict index保存proof無しを確認し、元DB/session共通Testやmethodを抽出しない。実scopeの全Main/calleeはreview済み、現時点Main変更不要。

自己所有のJDK ProxyでServlet Request/Response/Session interfaceを供給し、許可method以外はAssertionError。実SpringWebSession・session repository・DB・暗号codec・Login/Logout・random/token発行・API/MQ・Browser・HTTP・Root/VM・held四は呼ばない。メモリのpublic-before/public-afterはfixture識別子だけ、実session IDではない。CSRF入力A/B×64は公開固定形式canaryで秘密・認証・セッション発行は無い。Productionのparse/matchesは被検処理、expectedは固定literal/値・callback順/回数/不変。response methodは全拒否、state設定/外部資源取得は全拒否。

|Test ID|method|独立期待・観点|
|---|---|---|
|PT-WEB-CSRFPORT001|generatesFromSuppliedAttributeWithoutRandomnessOrExistingSessionRotation|既session無しfalse→trueだけ/固定名・header・persisted値、乱数0|
|PT-WEB-CSRFPORT002|existingSessionRequiresObservedNewIdentityAndUsesOnlyRotatedAttribute|既session時だけrotation、戻りID null/消滅/観測不一致/同値全拒否、old属性非読取|
|PT-WEB-CSRFPORT003|loadNeverCreatesSessionAndRejectsMalformedOrNonStringAttributes|非生成load、session/属性欠落null、型不正/63/129/空白拒否、正64|
|PT-WEB-CSRFPORT004|nullSaveInvalidatesOnlySuppliedExistingSessionAndNeverCreatesOne|null saveは存在sessionだけ一回invalidate、無し時非生成|
|PT-WEB-CSRFPORT005|saveRequiresExactHeaderParameterAndPersistedValueWithoutWritingState|正name/header/値だけ許容、誤metadata/不一致/不正値/欠落session拒否、書込み0|
|PT-WEB-CSRFPORT006|nullBoundariesAndMissingGeneratedAttributeHaveExplicitFailureSignals|null request/responseは固定nonnull契約、生成後session/属性欠落拒否|
|PT-WEB-CSRFPORT007|callbackFailuresPreserveIdentityWithoutRetryOrCleanupAuthority|callback Runtime/Error identity保持・再送/cleanupなし|
|PT-WEB-CSRFPORT008|concurrentSuppliedFramesKeepMaterializedValuesAndCallbacksSeparate|二worker八frameで値・callback・session相互汚染無し|

実行input003 prepare/static/run <frozen source>/post、JDK25.0.4・Maven通常20990 Core4217のprotocol/web jarを固定。Mainは全六通常NullAway20990・SpotBugs20992同byte、Testだけjavac release25/proc:none/lintall/Werror。classpathはprotocol/web/Jspecific・既固定Servlet6.1/Spring7.0.9/Security7.1.1/commonslogging/JUnit、DBdriver/Artemis/Bootstrap/Playwrightを置かない。compile/static全input hash/source、元XML/終了code、単一JaCoCo exec/通常Jar CRC/physical1・line/method/class/branch100、negative/null/例外/並行独立oracleを要求。全分岐未到達は未完、意味ないassertやprivate reflection/manual除外で埋めない。PMD/Checkstyleは全rawを保存し個別適用分類、抑制追加0。SDK/JVM syscall未測定、固定Console/JDK metadata閉包は現在argv/CP/init/XMLへ結合し、未知初期化は成功へ変換しない。

再試験は変更が必要な場合だけ新slotで行い、元failedsource/run/入力/coverage/exitを保持し合算0。障害は修正前915/916登録。厳格postと別source独立postでTest ID/元XML/source/Main/normalCRC/session/静的/全CP/guard/未初期化held四を照合。実CSRF chain/Browser/NK CHR/認証・controller組立/451/QA051final/正式1964-53/新WBSleafは全て別未完。結果063とmanifestに日時/branch/source/全command/OS/JDK/入力期待実際/coverage/BUG/path/hashを保存する。
