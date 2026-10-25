# Storage pure ResourceScope・当source単体テスト仕様

2026-10-25、sourcefd3d04df5710ca28f0e34f919cbc103e569a607b、主WBS-P003-08（原ResourceScope owner/cost）・関連P003-04（原StorageIoException、参照追加費0）、群STORAGE_PURE_RESOURCE27_V1、開始.5/2/6pp/cap10、freshused11/残89/reset1793513544、N/T/配賦/工数null。source/module名や変更担当で原Mainの主担当をP018等へ付け替えない。Program NK-OPS-001/NK-JMS-001/NK-SCN-001共通scope、RD OPS009/FIL001～009、UI237/251、SS333 SSC063/SSC308、既PT-OPS-RSCOPE001～008・PT-IOFACT-001～018・PT-F03-EXC005。

新Test/新ID/Production/oracle変更0。既ResourceScopeTest全8、FactoryResourceScopeTest全18、ExceptionValueContractTest一件の計27case/3suiteを当sourceへ資格化する。旧3c70 common44や全4222の成功確認再演ではなく、現候補の共通resource境界に必要な限定試験。source/Test byte同一の旧宣言inventoryだけ参照し、動的結果を転用しない。native/exec/Linux権限/実fileを含むstorage全moduleは実行しない。

## 期待値と安全判定

| 対象/既ID | 独立期待値・観点 |
|---|---|
| ResourceScope.use / RSCOPE001～008 | 成功はbody→close一回/42、未受理null portはclose0、nullable body受理、IOは固定reason/message/cause/suppressedなしへredact。unknown Runtime/NPE/AssertionErrorはidentity保持、既知body＋unknown closeはclose優先、unknown compoundは新redacted suppressionのみ。nestedはinner→outer close、自己64virtual taskは独立result/close64 |
| ResourceScope.acquire / IOFACT001～012 | port構築/全null契約はacquireより先、open null/取得失敗はbody/close0、成功open→body→close一回。unknownとIOの勝者/同一Throwable/prior suppressionを固定条件表で確認、closeの後条件/live=falseとredaction。OutOfMemoryErrorは明示newしたfixture値だけで実heap枯渇を起こさない |
| ResourceScope.handoff / IOFACT013～018 | 完成ownerを返した時だけ解放責任を移譲、完成時close0/不完全時一回close。独立3×4 golden winners SSRE/RRRR/EEEE・suppressed0000/0111/0111に一致、null complete ownerは拒否して解放、2並行ownerのtransfer stateが独立 |
| StorageIoException / EXC005 | 全Reason非null/固定message・causeなし、null reason拒否 |

対象Main/三Test・全helper（約944行）を読取点検済み。PT_DEFAULT：memory Token/list/atomic/callback/明示合成Throwable、自己executor/virtual threadsだけ。IO型はfixture exceptionで本物のfile/DB/JMSを開かない。公開Native/Root/permit/credential/鍵/VM/HTTP/OS service/RuntimeHook/ProcessBuilder操作0。callbackで実資源を取得せず、OutOfMemoryError/LinkageErrorも明示注入値。親unknown/native拒否操作の再試行やHOLD解除ではない。

同時実行は当new-only host JVMのみ、旧jobとsourceを混同しない。normal9694/source/hash/当main静的同byte9702を参照し再compile/static0。PG9738は旧固定decl27と現Test source/classを照合してmethod catalogを凍結、PG9740は27found/started/success・3suite/FESaborted/container failure0を要求しsafe XML/execへ。PG9742は当session/CRCと全ResourceScope/nested4interface＋StorageIoException/Reasonの7物理classを独立測定。non-executable interfaceの0/0を実測class100件数へ加算せず、raw四counterと適用性/未網羅/生成filter限界を分ける。旧exec union/除外/人工到達0。

障害は修正前915/YKT916、仕様変更必要なら上位分類を併用。Program単位の全PT・実JMS/resource/Root所有後条件/全451/正式/IT-STは別、正式1964-53/17-190/工数null/QA051final/全actualHOLD/G074493を保持。前Protocolの生成4/未到達16のstrict G01残は解消扱いにしない。source ownershipや関連参照追加費を二重計上せず、普通27件やcommitで止めず許可済み残PGPTへ継続する。
