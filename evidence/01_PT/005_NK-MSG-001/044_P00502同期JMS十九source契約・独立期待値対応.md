# P00502 all19 synchronous request reply contracts and independent oracles

NK-MSG-001。対象source/hash、承認設計commit/hash、独立期待値/TestIDは [PG29444](../018_NK-OPS-001/evidence/PG29444-p00502-all19-original-public-contract-v1/manifest.json)。

- P00502-ORACLE01 / ArtemisReplyConsumer.onMessage/isolateFatal/rollbackAfterFailure / JMS006,009,014: SS3217/SSC319332: publicnull/transactedpreflight unchanged; decode→atomiccorrelation→commit; permanentprotocol DLQsend+sameACKcommit→CommittedFatal. Knownproviderfailure rollback attemptedbeforecall/confirmedonlynormalreturn; nofalseconfirm/extraACK/retry. DirectError registrationowner doesbest-effortrollbackonce.

- P00502-ORACLE02 / ArtemisReplyConsumers.bind/start/deliveryFailure/ready/close / JMS014,WEBR319001..005: SS321SSC319332333: onecontext, preallocatedattempt/confirmed states resetperdelivery; confirmednonfatal onlybrokerretry, fatalgraph terminal/halted andnotifyonce/rethrow sameError afternotification, nosecondrollback ifattempted. Startupclose/directfatal table/finitegraphsecondary; serialclose phase flags onlyonsuccess, nativeUNKNOWNretainsouterowner.

- P00502-ORACLE03 / ArtemisReplyDlqSender.send/safeDeliveryCount/safeValue / JMS006,009: SS32110/11: no bodyread/reencode, sanitized allowlistonly/originaladdressqueue, transportmax128/canonicalUUID/layout8 orUNAVAILABLE, delivery>=1, persistentfixedDLQTTL, callerownscommit. Publicsend null/transactedreject; pureUUID parsecatch nonprovider.

- P00502-ORACLE04 / ArtemisRequestSender.send/sendOwned/rollbackAfterFailure/closeAfterFailure / JMS003,009,WEB321001: MQ022023/SS321: validateQprofile/correlation/bodylength beforecontext; BytesMessage persistentREQTTL5000/replyTo fixedaddress/protocol001, one send/commit; ownedcloseonce includingfatal, preserveexistingdirectcloseError priority/selfattachmentguard and classifygraphafterclose. No automaticrequest retry.

- P00502-ORACLE05 / CommittedFatalReplyException.constructor / JMS006,009: Cause-bearing internalcarrier after durablefatal isolation; fixedmessage, processnonzero viaowner, notordinaryretry norproofofDBtransaction.

- P00502-ORACLE06 / JmsContextFactory.open / JMS014: Functionalborrowedfactory returnscaller-ownedtransactedcontext; credentialnotexposed; actualopen/backendnotexecutedinpreparation.

- P00502-ORACLE07 / JmsReplyDecoder.decode/requiredArtemisAddress/requiredDeliveryCount/requiredProperty/parseUuid / JMS005,008,JMSR2659: MQ022023030/SS3218/232: Bytesonly, body0..1M beforecopy/getBody exact, permanentfixedreplyaddress orcanonicalFQQN, noreplyTo, lowerUUIDtext exact, property/header/length/profile/QSB S/A match. Provideracquisition outsidepuremalformedcatches; SDKfailures preserveidentity, noDLQauthorityfromdecoder.

- P00502-ORACLE08 / JmsRequestReplyClient.constructors/exchange/onReply/pendingCount/lateReplyCount / JMS007,010: SS3216/9: registerbeforesendonce, body256..1M, timeout1ns..2s, semaphoreinitial12/max20, registry20; sendergetsclone, timeout/interrupt/latefailure cancelandreleaseallpaths; IRQrestored; noautomaticretry. Producer2s calltimeout separate, no unapprovedendtoendtimer specchange.

- P00502-ORACLE09 / JmsRequestReplyException.constructors/reason/preserveFatal / JMS007,010,BUG2721: PrivateCAPACITY/TIMEOUT/INTERRUPTED catalog; finiteidentityvisited cause/suppressed/SQLnext/JMSlinked classifier rethrowssameError/noI/O. Cause-bearingoldcatalog notnewsecretlog. Wholehelperquality needsactualcurrentinputlineage, notoldclassassumption.

- P00502-ORACLE10 / JmsRequestSender.send / JMS003,007: Borrowedport transactedpersistent send boundary, callercontrolscorrelation/bodyclone; noadditionalbusinessretry/authority.

- P00502-ORACLE11 / MediaDescriptorWireClient.constructor/exchange / WEB-S3WIRE001..008: TrustedfixedAUDREQ01/VIDREQ01/MEDREQ01allowlist facade, HTTPcannotchoosecapability. Delegatesprotectedread/contextbinding, noimplicitpermissionorDBgrant.

- P00502-ORACLE12 / PendingReply.constructor/completion/complete/fail/toString / JMS008,CORRELATION006007: Ownedfuture neverexposed; eachcompletionthenApply clonesbytes, completionclonesinput, callercompletes/cancelsderivedviewdoesnotcompleteowner. ExplicitUUID/deadlinenonnull, bodyredacted, correlationdata notsessioncredential.

- P00502-ORACLE13 / ProtectedReadWireClient.constructor/exchange/requestPayload/decode/sameContext/Result / WEB166..173,238..245,BUG2721: Requestallowlist/norecords/nonnullcontext, timeout1ns..2s, UUID/header/NFCcodec, allrequest/reply/record/contextbufferswipe; expectedRSP/layout/correlation/currentcontext+resultprofile validated beforetypedresult. Outerknownprovidergraph classifiedbeforeUNAVAILABLE, pureclosedcodecinput/responsevalidation retainINVALID_INPUT/RESPONSE. NoHTTP/sessiongrant/retry/SQL.

- P00502-ORACLE14 / ProtectedReadWireException.constructor/reason / WEB238..245: FixedsecretfreeINVALID_INPUT/INVALID_RESPONSE/UNAVAILABLE, nonnullreason, cause/suppressiondisabled. Notrawproviderdiagnosticcarrier.

- P00502-ORACLE15 / ReplyCorrelationRegistry.constructor/register/complete/expire/cancel / JMS008,CORRELATION006007: Capacity1..20/strictfuturedeadline/duplicateatomic, completeexpirecancel singleremoval/permitreturn; atdeadline islate, notnewscreenresult; unknown/late metricexact; sixterminalorders andderivedfutureviewisolation whole7 alreadycurrentbyteproved, no confirmationrerun.

- P00502-ORACLE16 / ValidatedReply.record/body/toString / JMS005,008: NonnullUUID/body, inputandgetter cloned, bodyredacted. Purecopyvalue fromdecoder, notACK/session/authorizationproof.

- P00502-ORACLE17 / WebBrokerContexts.create/configureOwned/open/close / JMS-WEB001..003,FACT311001..003,334008: SS3216/SSC311334: fixedloopback/port1..65535/nk_webrole/12settings, allownerstatebeforefactoryacquire, configurationfailurecloseonce, borrowedpasswordcopywiped aftercreateContext. Startup/liveclosingknownfatalgraphs classifiedafterrequiredclose/onUnconfirmed; selectednativeUNKNOWNisnonreturn/retainsowner, no permissionfromlocalfixture.

- P00502-ORACLE18 / web.messaging.package-info.NullMarked / ALL_P00502: Nullabilitypackagecontract only, no executableMainmethods/coveragefabrication. Eachboundaryvalidatesnonnull andcloneownership; noNPEcatchnormalization.

- P00502-ORACLE19 / MqLoginClient.constructor/exchange/encodeRequest/decodeReply/Reply / WEB054..059,BUG2834: MQ021/036 UI226232234: loginonlyMQ noDB/passwordcomparison/sessiongrant, NFCtrimusername/NFCpassword/literalIPnoscopedIPv6,640request/688response, code0000/0200/0101/0106/9000 allowlist/contextusernamebinding/retryafter, original0200stillcurrentcontextprobe prerequisite. Allpassword/request/sentclone/reply/data wipedincludingunknowncallbacks. BUG2834knownJMS/IAE/ISE callbackgraph lostbeforeUNAVAILABLE isunfixedfinding; no normalreplay can certifyfatalnegative.

P00502公開19source1820行を全review、origin/main RD131 MQ021..036/UI231232234/SS321312311322323の個別method/入力/期待値/TestID19へ対応、485primary/costOwner全19一致。candidate8whole60定義はmetadata、Registry whole7のみ全body審査済み。Registry/PendingReply/Testの三入力が旧PG26456真正19成功と現byte一致で確認再演0、旧全体を現sourceへ転用しない。実EmbeddedBroker3wholeとWebBroker actual4/nativeownerはHOLD、他wholeはSDK/全body/sourcehistory資格前。MqLoginClientの既知callbackgraphがUNAVAILABLEへ縮退するBUG2834を修正前起票。Main/Test/compile/PT/実JMS/Root/native/DB/credential/actual4.class操作0。原/1 .087/.227/.455のみ準備完了、/2/190/正式451未受入、工数null。

実行: `python3 -B evidence/01_PT/018_NK-OPS-001/input/1941b_original_subdivided_artifact_contract_stage.py audit evidence/01_PT/018_NK-OPS-001/input/2314_p00502_audit_contract.json` metadata終了0。新規製品PT/coverageなし。原/1の準備だけ、原/2・451・元190未受入。独立期待値は公開設計の固定境界・順序・後条件に基づき、production methodで生成しない。正式1964PT/53scope・工数null。
