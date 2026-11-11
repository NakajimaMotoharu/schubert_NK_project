# Inspector原八・独立child六 実行前照合

2026-11-12、C02-R1、BUG2631/2632/2633。Production Main7aed不変。元InspectorDeploymentTest全八method/helper、UnitSyntaxFixture、wrapperのfake sh/od/cat、固定ShellCheck、独立SYSTEMD_UNIT_PATH内verify、realMainBridgeを確認。CLIの五Main source/公開入力・工具byteは既17500と一致。全empty-envによるCREDENTIALS_DIRECTORY欠落でfactoryより前に70、reserved agentなしでnative exporterなし。実DB/鍵/Root/service startやHOLDを試す実行ではない。

元profile oracleはmaintenance-owner追加と3→4。自己所有processだけfinallyのTERM後にfinite10秒wait、20秒本処理の割込も復元。新InspectorChildOwnerTestはProcess portだけで実child起動0。既dead/TERM→confirmed/未確認/呼出前IRQ/新IRQ/TERM失敗の六独立結果と10秒指定・destroy/wait回数・failure identity・IRQをassert。無期限wait/stream/exit-statusでの代用はfixtureが拒否する。Main/外部仕様不変更。

PG26082初static15raw/CS0保全。BUG2633の定数名/operand加算二件是正後、PG26086 PMD13rawはTest IRQ12と独立receipt literal1に個別非該当根拠、適用0/CS0/処理error0・規則抑止0。PG26088 preflightは未実行NOT_RUN。初metadataのMain-only manifestへpublic wrapper keyを誤要求したKeyErrorは製品0で保全注記、元resource receiptへ正しく別bindした。

次source固定後R2の原八＋新六を一回、元50tool receipt/全14XMLidentity/FESabort0/真正exitを独立確認する。Main coverage/正式更新を主張しない。

| Test ID | method | 独立入力・期待値 |
|---|---|---|
| PT-OPS-INBOX-OWNER001 | deadChildNeedsNoTerminationRequest | alive=false、destroy0/wait0 |
| PT-OPS-INBOX-OWNER002 | liveChildRequiresOneTermAndFiniteConfirmedWait | alive=true/10秒wait=true、TERM1/wait1/IRQfalse |
| PT-OPS-INBOX-OWNER003 | unconfirmedTerminationIsAnAssertionFailure | wait=false、固定未確認AssertionError、TERM1/wait1 |
| PT-OPS-INBOX-OWNER004 | callerInterruptIsPreservedAfterActualWait | caller IRQ=true、wait中clear・帰還後true、TERM1/wait1 |
| PT-OPS-INBOX-OWNER005 | newInterruptRemainsUnconfirmedAndRestoresNotification | waitがInterruptedException、同型失敗・IRQ復元、TERM1/wait1 |
| PT-OPS-INBOX-OWNER006 | failedTermPreservesCallerInterruptAndDoesNotClaimJoin | caller IRQ=true、TERM固定failure、同一exception・IRQ復元、TERM1/wait0 |

全fixtureはmemoryのみ・null collection要素なし・constructorでfinal状態固定、実Process/DB/鍵/並行taskを作らない。expectedは上表固定値から作成しproduction methodで算出しない。実行command/OS/JDK/source/終了code/hashは次R2 manifest、変更後結果は4011へ記録予定。Test用helperのみなのでProduction四coverageの分母追加0、shell/UnitはJava counterを転用しない。元8のID/期待値は本Program001 specのINBOX001～008とoriginal全methodsへ対応。
