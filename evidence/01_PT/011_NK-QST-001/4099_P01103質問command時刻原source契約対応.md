# P01103 質問command trace・UTC時刻 原1source契約

NK-QST-001。対象source/hash、承認設計commit/hash、独立期待値/TestIDは [PG27216](../018_NK-OPS-001/evidence/PG27216-question-metadata-contract-v1/manifest.json)。

- P01103-PG01 / constructor/messageId/correlationId/at / PT-CMD-META001,PT-CMD-META002: Trace UUID message/correlation independentlyrequirednonnull withliteralnames, preservedasprovided (neednotbedifferent). Instantnonnull; noowner/token/password/key authority orcanonicalization oftracevalues. Metadataisnotoperationtoken/HMACimplementation. SharedP00601/P00703 closure remainsrequired.

- P01103-PG02 / constructor/at / PT-CMD-TIMEBOUND001..003: UTCyear1to9999 inclusiveafterfloortruncatetomicros: loweraccepted,+999nsfloorloweraccepted,-1nsrejected; upperaccepted,+999nsfloorupperaccepted,+1000nsrejected. PreEpoch .999999999 floors .999999, epoch+1nsfloorszero. ExpectedfixedInstantliterals independentofproductiontruncation.

- P01103-PG03 / toString/accessors / PT-CMD-META002: ExactconstantQuestionCommandMetadata[REDACTED] fordistincttraces/time, noUUID/time/providertext. Allaccessorspreservegivenidentities/nanosfloor. Valueisimmutable/JDKonly/noresource/SQL/threads. ActualHMACcurrentowner/constanttime/samepayloadfrozenInbox7days notprovenbythisvalueclass; no oldproofsemantictransfer.

P01103 actualownQuestionCommandMetadata1を全文確認。SS324 headerID/time/contextはHMACpayload外、Metadataはtrace/time純値に限定しHMAC/token再送の共有P00601/P00703完了を転用しない。nonnull名前/UUID保持/UTCmicro床切詰め/year1～9999/前epoch/固定REDACTEDを独立literalへ対応。既wholeMetadataContract2/TimeBoundary3全source確認/JDK-only候補、今群は実行0。原/1準備のみ、原/2には現source通常5資格と共有HMAC/Inbox終了条件が必要。

実行: `python3 -B evidence/01_PT/018_NK-OPS-001/input/1522_question_metadata_contract_audit.py` metadata終了0。新規製品PT/coverageなし。原/1の準備だけ、原/2・451・元190未受入。独立期待値は公開設計の固定境界・順序・後条件に基づき、production methodで生成しない。正式1964PT/53scope・工数null。


追加証拠照合PG27218: 既PG19008全5成功の元source f85525/b093・sessionを保持し、Main/Test3 source hashと現正常compile対象Main1のphysical hash不変を確認。旧namedsubproof23362へ接続、四100はその元sourceに保持。確認目的の再演なし・新試験実績0・新source全域資格0、実HMAC/Inbox終了依存未受入。費用は当原群の照合内、新通常5再試験群は未着手/加算0。
