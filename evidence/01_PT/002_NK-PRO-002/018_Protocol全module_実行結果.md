# Protocol全module・当source実行結果

2026-10-25、sourcefd3d04df5710ca28f0e34f919cbc103e569a607b、群2212/017。全Protocolの102通常@Test/22suiteを一回実行し、全成功・F/E/S/aborted/container failure0。既96宣言＋先行PAGE3/SEM3をcurrent source/class byteへ照合、新ID0。全102のsafe XML/summary/source/hash/時刻/OS/JDK/command/真exitを下記へ保存。compile/static/旧4222全体成功の確認再演0、normalのsource/class/jar/fixtureはread-onlyで保持。

| 本Program evidence/provisional配下のmanifest.json | SHA-256 |
|---|---|
| PG9720-protocol-module-preflight-v1 | 97b3f79828efef6b07a49de2505d1a6fc8f07520b714acdfb6aadf01f51855a3 |
| PG9722-protocol-module-host-v1 | ddcc4a3ae1644a15b61365e645af41e26e4d255d936be1ed008ce42a87d80692 |
| PG9724-protocol-module-post-v2 | 5eb3672c1838e6ef522e57f724392e946c437b0499967f7623d889504227cd77 |
| PG9726-protocol-generated-shape-post-v1 | c5e2b600dfadfca7c1a8a889fec5d605e775b7e75e36955bc4a70cf5298290b5 |
| PG9728-protocol-counter-count-correction-v1 | d8acceac54b0b8e6edafd0ba15c4039adf9f5a15408e5f5ca8f13fc77129e6f2 |

## 実測と非該当を区別する

全Protocol jarの物理176classをhash付きinventoryへ含め、元execの単一session/実class CRCと独立照合した。JaCoCo0.8.15の標準集計はline3480/3480・method743/743・class159/159・branch1014/1014、全missed0。ただし、このraw集計を「176class全部が個別100%」「compiler生成命令まで全部実行済み」「451合格」と表現しない。

| 分類 | 物理class数 | 根拠/扱い |
|---|---:|---|
| 実測counterを持つclass | 159 | LINE/METHOD/CLASSの対象が実在し各miss0、branchなしは自然非適用。個別四100の実測件数159 |
| 実行Codeのないinterface | 6 | JDK ClassFileの全methodにCodeなし。FieldValue/LayoutPayload/PayloadData/PayloadRecord/ProtocolId/WireEnum、raw counter0/0、成功件数へ足さない |
| package注釈metadata | 7 | package-infoのfields/methodsとも0、JSpecify境界。全physical inventoryに残し、JaCoCoが報告しない7件を0missの人工counterへ変換しない |
| 標準filter対象compiler switch-map | 4 | synthetic、$SwitchMap$ field、clinit一件の実byteを確認。raw JaCoCo四counter0/0、実execにhit25/miss16 probe、個別四100/厳密生成命令網羅へ算入しない |

元PG9724v2のfour100ExecutableClassCount=163は0/0のswitch-map四件を含む誤label（BUG1759）。元manifestを上書きせずPG9728で159へ追記訂正、全169report行と4正/4不正vectorを実確認した。先行75classは全LINE/METHOD/CLASS対象が実在し、全75四100は非影響。原raw counter/試験件数/費用は変えない。

## 残るG01/451判断

4compiler helperのraw未到達probe16を0に補完せず、`strictGeneratedInstructionCoverageQualified=false`。対象はPayloadCodec$1、MediaDescriptorValidator$1、FieldDefinition$1、LayoutFieldCatalog$1。既定JaCoCo標準filterの測定限界を開示し、source-level全raw counter達成と厳密compiler生成例外/命令条件の受入を分離する。新たな除外設定/到達不能偽装/意味のないassert/品質免除は行っていない。生成codeの適用性・要求coverageへの影響を最終G01/451レビューで解消するまでは全品質受入へ算入しない。現moduleの全method/要求/oracle trace、F03 legacy解析適用性、全scope/source/run・CHR/native等も別の残条件である。

## 工具是正と保全

BUG1758/YKT1509：post v1はmetadata名package-infoのhyphenを普通型regexで拒否しmeasure JVM/親post実1、成功manifestなし。元Python55fac127/Java1daa6574と作成済みslotを保全。v2は全176を解析し、JDK Code属性で7package/6interfaceを非実行と実証、名前だけのmetadata免除不可・1正/5反例、全code-bearing/extra/CRC guardを維持した。先行75class scopeと全byte static比較はmetadataを対象外に隠したわけではなく選択source unitに含まれず非該当。元102を再実行せず独立postだけ是正。

BUG1759/YKT1510：0/0誤計数を修正前登録しclass_counter_applicabilityの4正/4不正vector・全169行/旧75行で独立再計数。raw0/0・測定対象欠落は実測PASSではなく、branchlessの自然0/0だけはclass/method/lineの実対象を確認して許容。未到達16/原誤label/原失敗を保持。両工具scopeは検証済み・修正commit/remote具体化待ち、製品仕様違反や新製品PASS数へ転記しない。

起動前のbindings hash手転記の余分文字によるread-only assert失敗は、原9592公開manifestの実hash ae17aff...ffc8bと照合して是正、metadataを改変せず実job前の選定手戻りとして保存。元host39103/v2post64362/generated95499は真正終端0、v1は前述実1、他有限postも終端0。VM/Root/DB/JMS/鍵/配備操作0・外部所有未照合HOLD。主WBS-G01、元/関連Programの主担当や費用を再配賦しない。開始1/4/9cap10、fresh12:14:24UTC used10残90/reset1793513544、共有丸め差0≠専有費、N/T/配賦/工数null・usage34e51009。正式1964-53/17-190/QA051final/全actualHOLD/G074493/現WBS監査HOLD不変。次は追加Testの現source登録/trace又はStorage等の許可済み独立PGPTへ進み、このraw module達成だけでは停止しない。
