# Login失敗handler 自己所有HTTP境界単体仕様

Program NK-WEB-001、WBS-P007-06、FUN-001/AUT001..004/MON004、UI226/232/252、SS313/314§5.2/351/352、QA055/UIC012/SSC338、BUG2340/YKT2085。対象MqLoginFailureHandler constructor/onAuthenticationFailure全1source/1physical。既web115はDB-backed BeforeAllを含むため抽出/再演せず、original seed NOT_IN_CURRENT_MEASUREMENT_REGISTRY・既PG20458 knownProofs空を確認して新自己所有境界を定義した。

固定public RequestID UUID/数値documentation IP192.0.2.1/ClockとMemory System.Loggerだけを使い、JDK HttpServletRequest/Response interface Proxyでresponseと監査を捕捉する。requestは内部context属性読取だけを許しbody/username/password/session/header取得はAssertionErrorで拒否。実Login/資格/認証/session/ネットワークendpoint/Browser/Caddy trust判定/DB/JMS/Root/VM/鍵/held4無し。contextのpackage-private constructor使用は自己所有callback限定のfixtureで本番権限や経路の変更ではない。InetAddress.ofLiteralの数値だけ（hostname/DNS/connectは使わない）、SDK/JVM metadata/syscalls全0は未測定。

期待値は承認UI226/SS314351352/QA055から独立HTTP literalと監査schemaへ定義する。API確定秒0..900を整数headerへ渡し302/login?locked、画面文はUI226固定15分（別PG21044）。Production変換methodを呼んでexpectedを生成しない。固定文・Current baseline・DIFを変更しない。

|Test ID|method|観点・入力・独立期待|
|---|---|---|
|PT-LOGIN-FAIL001|lockedApiDelayIsExactHeaderWithCurrentRedirectAndOneRedactedAudit|0/1/899/900 →Retry-After literal/Location/302・監査1/requestID/route/retry一致、-1/901は型境界拒否|
|PT-LOGIN-FAIL002|badFormProxyAndServiceFailuresRemainDistinctClosedHttpOutcomes|bad302/error/audit1、form400/audit0、proxy403/denial1、service503/audit0、lock以外Retry-After無し、診断非反映|
|PT-LOGIN-FAIL003|nullAndMissingInternalContextNeverProduceSuccessfulResponseOrAudit|constructor/request/response/failure null、context欠落/未知型→明示拒否、headers/status/監査へ成功を作らない|
|PT-LOGIN-FAIL004|memoryAuditFailurePropagatesBeforeLockedOrBadCredentialResponse|own memory audit sink例外同一性、response変更0、イベント未保存。実ログbackend無し|
|PT-LOGIN-FAIL005|responseCallbackFailuresKeepTheirIdentityAndDoNotBecomeCompletedRedirects|二header/status callback故障は同一runtime、form/service sendErrorは同一IOException、未完status。先行監査が既保存なら保持しHTTP成功と混同しない|
|PT-LOGIN-FAIL006|sharedHandlerParallelCallsKeepOwnDelayHeadersAndRequestAudit|共有handler二worker16、固有delay/header/requestID監査16、混線/重複0|

null/正常/境界/異常/例外/並行を新全6同source一run、F/E/S/flaky/abort/not-runを成功算入0、全physical LINE/METHOD/CLASS/BRANCH未網羅0/単一CRCsession/合成除外無しで確認。再送・transactionは当失敗HTTP handlerが業務要求を再発行しないため非該当、Inbox/MQ再送成功へ転用しない。current normal20990/六SpotBugs20992のMain4217を全1035入力/byteで拘束し、対象Main＋新Test PMD/CS、CP/Gson/Spring/JDK/元class-initの限定閉包と四heldprobe0、独立post/traceを照合。Source/環境/日時/command/OS exit/input/actual/counters/BUG/hashは各manifestと061結果に記録。

Command: 018/input012 qualifier prepare/static 097 profile →source固定→run→post→独立post。新Mainの製造変更はなく不要な六Main build/旧モデル5source FOUR100の確認再演はしない。PG21058 raw5のうちproxy index条件1はBUG2370/YKT2115へ修正前起票し定数化、raw4の個別非該当を記録する。実Browser/CHR-A01/同source全451/正式1964PT53scope/leaf終了依存は別途未受入。
