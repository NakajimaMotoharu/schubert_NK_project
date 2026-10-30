# 2933 Web入力・MockLogin原whole八・現source限定PT仕様

source6b53/normal14216/current1831固定。原WebStartupInputsTest4とLoginControllerTest4を一fresh自JVMで実行する。NK-OPS-001/SYS002004/UI243253/SS342343§4～6/PT-OPS-WEB-INPUT001～004、NK-WEB-002/FUN001-SYS001-AUT001/UI222226264/SS313355/PT-SCR105～108/QA045-UIC005-SSC074。対象Main二Source三Code（WebStartupInputsとValues、LoginController）の全Jar closureを測定、元baselineP01806/P01601・TestUNKNOWN保持。群3318主P01806/関連P01601、元0.75/3/8pp一群固定、component追加0/実配賦null、新cohort資格を新設計/機能/受入へ加算しない。

全Main/Test、WebConfigurationLoader/Bootstrap WebNonSecretConfig、ServiceCredentialLocation/Contents・Service nested型/ChildStartupContextの既知純helper、WebMvcConfigurationの明示全beans/初期化、ErrorController/MenuController/ProblemViewFactoryのconstructor、固定login template全文を確認。production loader/native/credential取得/認証filter chain/実server/socketへ結線しない。WebMvcConfigurationはcomponent scanをせず明示表示beansだけ、classpath:/templates/と閉view名でresolveする。実Browser/CHR/IT/ST受入は対象外。

| 元whole Test ID / method | 独立期待値・正常/境界/異常/null/並行再送適用性 |
|---|---|
| WEB-INPUT001CombinesIndependentFixedInputs | Mapのconfig/credential location文字列とsupplied sourceだけ、DEBUG/8080固定・WEB層/読取1回・Path一致、DB/鍵fileを開かない |
| WEB-INPUT002MissingPrivateLocationStopsBeforeSourceRead | CREDENTIALS_DIRECTORY欠落は固定例外、supplied source read0 |
| WEB-INPUT003SourceFailureAndConfigAdmissionStayDistinct | 単純StorageIoException identity、誤config rootはsource実行前に固定拒否 |
| WEB-INPUT004NullContracts | source/map/Values null拒否、非秘密default parseでSHA256を実行；validateEnvironment wrapper未実行なら未達保持 |
| SCR105ApprovedBrandAndPostCsrf | Mock GET200/UTF8、lang ja/title「schubert NK - ログイン」/h1、POST/login formと合成CSRF hidden各1 |
| SCR106InputsAndNoLeakedCredentials | labels/name/autocomplete/required/autofocus、password入力値は空、submit「ログイン」 |
| SCR107OnlyMatchingCurrentMessagesAppear | error/locked/logoutの現行三literalを各単独表示、unknown/欠落は無表示・passwordは毎回空 |
| SCR108ClosedViewAndControllerBoundary | controllerはloginを返す、許可view以外/fragment/path traversal/redirect/forwardはresolver null、Mock POST/loginは405（認証成功とは別） |

独立期待値は元Testの明示HTTP/DOM/string/Map値とUI/承認SS正本。期待値をProduction methodで生成しない。元TestのgetLoginは実際値を得る操作helperで、expectedは固定literal。MockMvcの応答値は元assertionと真正XML結果で照合し、捕捉HTML/screenshotが無いのに存在すると記録しない。空表示/合成CSRFは公開fixtureだけ。入力composition/GET viewにはDB再送/業務並行/TXは非該当、actual session/本番CSRF/credentialは発行しない。

effectは非秘密canonical設定のSHA256実行true（鍵無し）とnormal Web Jar内immutable public login template読取true。actualPrivateFilesOpened/actualSecretKeysLoaded/actualCredentialValuesUsed/actualAuthenticationOrSessionIssued=false、mockMvcOnly=true/actualBoundSockets=0/actualBrowserActions=0/characterizationAccepted=falseを専用postで明記する。SDK内部bootstrap/evidence hashは元Product/Test bodyの効果domainと別。旧API15342誤記のpostDisclosureCorrectionsを引継ぎ、sharedpurev3へcrypto/resource処理を強行しない。

command：python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg15486_web_inputs_mocklogin_eight_pt.py。rawと専用15488post draftを事前lint0で用意、元真正terminal/実RAWhash取得後にpostを初回実行。全current/snapshot/Input/Jar/Test/launcher/reporter・login.html ba814effをpinし、一新session/180秒上限、全8XML/FES/OS-JDKprefix/全三CodeCRCを検証。coverageは全二Sourceへ集計し、line/method未達/branch自然0はそのまま保存・人工100/手動除外/旧exec union0。元fixed passive readerで四held class true probe無しを確認、reader selftest/旧PT確認再演なし。別15490独立postで元8ID/全code/SS-UI/期待値/packaged resource/typedcounter/効果/owner/実stagehash・意味反例を照合する。結果2934/実manifestに実日時/JDK25.0.4/OS/branch/source/command/終了/全hash/coverageを保存、正式1964-53/歴史17-190/工数null/QA051final/全HOLD不変。

初回15486/4b7d6ea4はFiles部分文字列がServiceConfigFiles型へ一致してpreflight1、SLOT/compile/JVM/OUT前停止。BUG2131/YKT1878を修正前起票して旧工具を保持し、new15487v2は識別子境界regex・ServiceConfigFiles二許可/Files三禁止のmetadata反例を先行確認、同じ元見積/原8Testで初回Product実行へ進む。実commandはpython3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg15487_web_inputs_mocklogin_eight_pt_v2.py、専用15488draftのoriginal import/RUNもbody実行前にnewv2へ合わせる。新PT成功を旧未実行8の再試験成功へ二重加算しない。
