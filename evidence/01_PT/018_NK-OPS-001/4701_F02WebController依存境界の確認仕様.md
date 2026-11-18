# F02 Web Controllerの直接依存境界

NK-OPS-001、WBS-F02-a、SYS-005/014、SS311 §2、§3、§5.2。対象は静的検査器 `ModuleDependencyAudit`。BUG-3328／YKT-2701。製品Coreは `ecf8a00fbd37720b80f8e107d59727723c706a12`。独立期待値はSS311の禁止・許容事項と、合成classの明示的な参照先から固定する。

| Test ID | 合成入力 | 期待する直接参照 |
|---|---|---|
| PT-F02-ARCH-001 | Controllerから通常のFacadeを呼ぶ。Facadeは内部にJMS型を持つ | 指摘0 |
| PT-F02-ARCH-002 | Controllerが汎用OutputStreamを使う | 指摘0 |
| PT-F02-ARCH-003 | ControllerがJDBC Connectionに依存 | Connection |
| PT-F02-ARCH-004 | ControllerがStorage moduleに直接依存 | Storageの型 |
| PT-F02-ARCH-005 | ControllerがSpring JmsTemplateに依存 | JmsTemplate |
| PT-F02-ARCH-006 | ControllerがJakarta JMS Messageに依存 | jakarta.jms.Message |
| PT-F02-ARCH-007 | ControllerがJavax JMS Messageに依存 | javax.jms.Message |
| PT-F02-ARCH-008 | ControllerがFiles.existsを呼ぶ | Files。シグネチャ上だけのPathはこの呼出しの指摘に含めない |
| PT-F02-ARCH-009 | ControllerがFileChannel.sizeを呼ぶ | FileChannel |
| PT-F02-ARCH-010 | ControllerがFileを直接構築する | File |
| PT-F02-ARCH-011 | 名前にControllerを含まないRestControllerがPath.ofを呼ぶ | Path |
| PT-F02-ARCH-012 | 名前にControllerを含まないSpring ControllerがJMSに依存 | javax.jms.Message |

手書き24 classの合成JAR六個をJava 25で準備。初期化の検知値を一つ仕込む。JAR importと依存辺・直接callの読出だけを行い、クラス本体を実行しない。JAR名と全class件数、5規則、各origin/targetを一致確認し、四別規則は合成入力で0件を要求する。期待違反を含むため子ArchUnitは真正終了1。検証側は期待集合と終了値の一致だけで終了0。初回の旧工具と修正後の工具を別source・別runで保存する。合成静的確認であり、製品六JARの実証、通常製品PT、全451、実測coverageは別工程である。
