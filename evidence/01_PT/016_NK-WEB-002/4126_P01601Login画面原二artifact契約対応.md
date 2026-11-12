# P01601 SCR001 Login画面・承認title・固定lock文

NK-WEB-002。対象source/hash、承認設計commit/hash、独立期待値/TestIDは [PG27580](../018_NK-OPS-001/evidence/PG27580-login-screen-contract-v1/manifest.json)。

- P01601-PG01 / LoginController.login/GETlogin / PT-SCR-105,PT-SCR-108: GET/login returnsfixedtemplate login only, no businessconnect/no formbinding/noauthcredentialread. POST/login belongsSecurityfilter, displaycontroller alone doesnotauthenticate; MockMvcwithoutfilterPOST405. ExplicitWebMvcConfiguration registersLogin/Menu/Erroronly/nocomponentscan, templateprefix/suffix/UTF8/HTML/cache/checkExists/closedViewNames/no redirect-forward/partialoutput, CSRFprocessor fixed. WholeLoginControllerTest4+allhelpers/config sourcefullyreviewed, ordinaryMockMvc possibleclosedprofile only; noHOLD extraction.

- P01601-PG02 / login.html title/form/input/navigation / PT-SCR-105..106,LOGIN-DISPLAY-PORT: QA045/DIF001 approvedtitle schubertNK - ログイン, h1schubertNK, ja/UTF8/viewport/css, visibleuser+passwordlabels, POST/login+resolvedhiddenCSRF, userrequired/autofocus/autocompleteusername, passwordtypepassword/required/autocompletecurrent-password/emptyredisplay. No password/token/context in responseorlog. Fixedtitlechangeonly CHR-A01 allowed; Currentbaseline untouched.

- P01601-PG03 / login.html locked/error/logout / PT-SCR-107,LOCKED-LOGIN-DISPLAY: Queryerror=>fixedincorrectcredentials; locked=>Current固定「ログイン試行回数が上限に達しました。15分ほど待ってから再度お試しください。」; logout=>fixedloggedout; unknown/noquery=>nomessage; passwordremainsempty. QA055 approvednoactualremainingtimeinDOM/noGETdynamicstate/newDIF. Real0..900secondsRetryAfter isAPI/Loginhandler headercontract(notthesefixedwords); actualHTTP/auth/CHR remainsseparateunacceptedending.

- P01601-PG04 / existingPG24416DOM28/82snapshots / LOGIN-DISPLAY-PORT,LOCKED-LOGIN-DISPLAY,USER-TEMPLATE-DOM: All10 inputsource/Test/toolsand4resourcehashes unchanged; old28success/82publicDOM snapshots retainedoriginalsource3814a5/Main7aed, nojavaMainonCP/javaCoveragenull/fullMockMvcBrowserfalse. No repeated28/no oldexecunion/currentprojectsourcecertification. ActualLogin/authDB/session/RetryAfter/CHR/P01502/451 remainopen; byteconsistency alone noacceptance.

SCR001 ownedLoginController/login.html全文とSS313314355/UI222226264現承認を対応。QA045title/h1新名称、POSTfilterとGET表示分離、閉view/UTF8/CSRF/username属性/password空再表示、error/locked/logout固定表示を明記。QA055Current固定15分文は実残秒ではなく、0..900秒RetryAfterは別API確定header責務。wholeLoginControllerTest4+explicitMVC設定を全読取、既PG24416全28/82DOMの入力10/resource4hash不変を照合し旧source限定参照/再実行0/Java架空coverage0。P01502/実認証HTTPheader/実NKCHR/同source451終了未受入、原/1だけ完了。

実行: `python3 -B evidence/01_PT/018_NK-OPS-001/input/1700_login_screen_contract_audit.py` metadata終了0。新規製品PT/coverageなし。原/1の準備だけ、原/2・451・元190未受入。独立期待値は公開設計の固定境界・順序・後条件に基づき、production methodで生成しない。正式1964PT/53scope・工数null。
