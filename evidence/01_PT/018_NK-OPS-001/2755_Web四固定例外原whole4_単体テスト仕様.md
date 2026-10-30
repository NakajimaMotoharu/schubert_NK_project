# Web四固定例外 原whole4仕様

2026-10-30、主F03・関連Main owner参照のみ追加0、着手前.5/2/4pp、source6b53/normal14216。SS314/324/333/352、QA050/BUG1482/YKT1237。logging/revocation/media/sessionの各ExceptionValueContractTest原whole1をそれぞれ一fresh JVMで実行し、coverage execは合成しない。全Testと全直接Main/Reason/initializerは全body既読。暗号化payload例外という名称でも実crypto/key/providerを呼ばず、固定値型だけ。実session/log/revocation/media/HTTP/JMS/DB/VM/Root/ファイル操作なし。

|Test ID/method|独立fixture・期待値|whole Source|
|---|---|---|
|PT-F03-EXC006/exc006LogReasonsRetainOnlyTheClosedDiagnostic|既各reasonに固定prefixと閉じたreason名、cause null/reason同一、null reason NPE|WebLogPayloadException/Reason、P006-04|
|PT-F03-EXC011/exc011RevocationReasonsRetainOnlyTheClosedDiagnostic|同様にrevocation fixed prefix、null NPE、causeなし|RevocationPayloadException/Reason、P015-05|
|PT-F03-EXC007/exc007MediaStatusAndRetryRemainClosedAndNonNull|fixed media message/status503、BUSYのみretry1/他empty、reason同一/causeなし、null NPE|MediaDeliveryException/Reason、P009-04|
|PT-F03-EXC013/exc013SessionReasonsRetainOnlyTheClosedDiagnostic|session fixed prefixと閉じたreason名、causeなし/null NPE|SessionPayloadException/Reason、P015-01|

固定prefix/503/1をproductionから生成しない。reason列挙の網羅性全域や外側機能を本群から推定しない。pure値型で資源競合・再送は本群非該当。全四Source各二physical、元838のSource/caseと重複なし。各元Test hash/正規module/package/normal snapshot/Launcherの選択を実前検証し、各suiteの原一methodを全実行、F/E/S/not-run0。最小一method用の資格済postv2でそれぞれ一session/CRC/全closure/八metadata反例/原環境/全input・六Jar/static14224を確認する。自然branch0はN/A、未達は保持。

commandはPYTHONPATH=tools/qualityでchecked entryへ各pg14718/14720/14722/14724_web_*_exception_one_pt.pyを指定、後続各14719/21/23/25の独立post。実行日時/branch/source/commit/OS-JDK/command/exit/入力期待case/実XML/exec/counter/owner/hashは各manifest、結果2756。旧成功の確認再演0、正式/工数/全HOLD不変。
