# Web監査JSON・Transport属性 単体仕様

NK-WEB-001 / WebSecurityAudit(record/version/canonicalAddress/Route/Event)、CaddyTransportContextFilter(constructor/doFilter)。AUT001～004/MON004/FUN001、UI222/226/252、SS313/314/342/351/352、411/451、757。WBS-P00604/P01502へ関連付け、費用は一群だけ・Source/Test/親へ配賦しない。原57line/6method/1class/51branchと11line/6branchの部分未達を、当正常Mainの必要な全Source単位で資格する。旧正式8587からLogout event/invariantとidentify属性連携が変わっており、既成功の確認再演ではない。Main PGは既実装review、実障害以外でコードを変えない。

|Test ID|class/method・入力と独立期待値|
|---|---|
|PT-WEB-TRANSPORTPORT001|CaddyTransportPortTest#trustedDispatchAndRedispatchKeepOneIdentityAndSameContext。loopback/https/単forwarded、初回context/内部UUID、二回目同identity/context、logger0|
|PT-WEB-TRANSPORTPORT002|#nonHttpRequestAndResponseAreRejectedBeforeAnyDispatchOrAudit。非HTTPのrequest/response各々ServletException、生成/属性/chain/logger0|
|PT-WEB-TRANSPORTPORT003|#deniedPeerEnds403OncePerDispatchWithoutErrorRedispatchOrTrustedContext。非loopback又はForwarded禁止、403/chain0/sendError0、proxy拒否の閉じたJSON一回、再dispatch同内部UUID|
|PT-WEB-TRANSPORTPORT004|#existingContextCannotBeReboundToAnotherClientEvenWithSameServerId。既contextとforwardedIP違い、403/旧context維持/chain0/一audit|
|PT-WEB-TRANSPORTPORT005|#contextSaveFailuresAndNullContractsStopBeforeDownstreamWithoutUnsafeFallback。全nonnull境界、属性保存IArg/IState→固定例外/原因0/旧IDだけ保持、chain/logger0|
|PT-WEB-095～100|既WebSecurityAuditTest全六methodの独立JSON literal/closedイベント・route・retry0..900・canonicalIP・unicode/secretcanary排除・clock/logger失敗伝播・不変/100並行。既fixture/source/oracle不変更|

fixtureはServlet interfaceのProxyと属性Map、recording System.Loggerだけ。実Caddy/HTTP server/socket/DNS/ブラウザ/DB/VM/Root/session/鍵/ファイル/Artemis/project FFMは使用しない。標準JDKのIP literal/scope解析を実Caddy/認証資格にしない。新Loggerは閉じたliteral JSON全keys/valueを照合し、Throwable overload/未知request method/sendErrorは即fixture失敗。expectedはSSのliteral表で、productionから生成しない。null negativeは411 non-null guardの拒否でありproductionでNPEcatch/正常化なし。

予定11method/2Testclass、Main4physical（WebSecurityAudit/Route/EventとCaddyFilter）全報告。PG18642正常artifact/NullAway、PG18648六Main SBは全input/jarhash一致で再利用。新旧二Testclassのみcompile/Main2＋Test2のPMD/CS、全class選択JUnit/新単exec/session・独立source/XML/CRC/fourcounter post。実Caddy/認証・API DB audit/全WBS/451は残す。環境・command・時刻・source・元失敗・BUG・hash・coverage・結果を037/manifestへ保存し、失敗/未実行を合格へ加算しない。
