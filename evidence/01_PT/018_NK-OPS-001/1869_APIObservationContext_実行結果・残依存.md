# API観測・SDK assembly 限定実行結果

2026-10-25/1868/PG-D636/group2100。現Production cb91bc2ec0ef5a36652369aff5c86fa037801cca 未配備。開始4/7/10pp/cap10/fresh56残44→08:22:57 fresh57残43/reset1793382075、共有差1/専有費・他chat内訳・N/T・工数null。元/v4/v5不変更、usage2e446b3d2f2d6a4d21ed5cab84b65c5b641781ec161df7f580f2886cadffd65eはexplicit record欠測であり0費用ではない。

| 正本manifest（evidence/provisional配下） | SHA256 | 限定結果 |
|---|---|---|
| PG9154-api-observation-context-six-compile-v3/manifest.json | 3ad165657e7b7dda87fc795b505063b2276b64b34b521fcb09070b3c68d7c5fd | normal六module/exit0・Compiler/NullAway/format等、PT0 |
| PG9156-api-observation-context-host-v4/manifest.json | cc25b55bda084d954b75a1000720e78eef582c83d08f028915f9d2f2a4903584 | 実26/1suite/OBSCTX001～026、F/E/S/aborted/not-run0、fresh own JVM exit0 |
| PG9155-api-observation-context-static-v4/manifest.json | 94cc1a6c840b15672d13478cb5b81e579ffa52960b5b22b55509e5684fa94059 | raw exit1/PMD4-exit4、CS-SB0、元raw保持 |
| PG9157-api-observation-context-review-v1/manifest.json | a728b7c177342e3d6f9931daa0b1b8bd3d2fcdf10bc8c2977c7bb33014e17eb6 | 各native failure-frame catch四行をsource/全XML/正式SSへ結合・未分類0/抑制0、6metadata反例 |
| PG9158-api-observation-context-post-v1/manifest.json | f2729d1e3eb68429dd43494d1ab737bd878dc08e113c963932197a2f6abbd385 | 全新一Main L58 M7 C1 B20未網羅0、CRC0/session1、7receipt反例 |
| PG9160-api-observation-context-trace-v1/manifest.json | 33d6811f8d10422d348f404c8269f689295c1e57f0dbd3e033b9e312e61849f1 | 全1842Main・旧1841同byte/246canonical owner/五arch0、15metadata反例/他25caseと共通fixture保持 |

Test別入力/fixture/独立literal oracleは1868表と同名Test。実command・OS/JDK25.0.4/tool/dependency/input hash・XML・case結果・時刻・終了codeは上記当runへ一意対応。session PG9156-API-OBSERVATION-CONTEXT-V4、append/旧exec移植/除外0。helper fixture outer五つはcompile-only、私有JVM Threadとtyped fake JDBC/Clock/beanだけを用い、borrowed Poolの操作はgetConnectionのみ。実API Main/既サービス/VM/Root/DB/native/鍵/配備は新操作0。普通Thread回収をactual資源解放やHOLD解除に読み替えない。

保持済みassembly→SDK initialize→DEBUG worker一回を接続、STDはworker/SQL/clock/bean/remaining未読。正常cleanup後だけliteral 3/5/7件・2/4/6秒をSDKに供給。元remaining supplierを借りてworker停止確認→SDK close、期限/競合/再入/例外のUNKNOWNは永久保持・SDK/Pool後続解放なし。個別PMD四catchは元primary/diagnostic graphを保持しmandatory UNKNOWN記録後に同object/fatalを伝播する必要箇所、全catch抑制やraw0にしない。CS/SB実0、部品四100は全source四100/451受入ではない。

## 原失敗・修正・横展開

| BUG/YKT | 原結果/原因 | 是正・再試験・全対象/非該当 |
|---|---|---|
| 1736/1487 | ca4254abd、9154v1原d76c6ca21fa277a564dede6c14f437f47bbe6eb760938132cff30e19cec9a21e正常六0→9156v1原be147945c62929a84d3349d9b95925906d4a5f4e27db895f79c73341740220cb実26/F1E0S0。016がworker由来例外へassembly文面を誤期待 | c06a72ef46bb65c091de329468f70dd5d347ce4eでTest016だけ初回worker literal/同policyobjectと再close assembly literalへ是正、Production変更0。9160が他25case＋共通fixture完全保持を実証。022等はassembly自己拒否、017～021/026はsupplied identityで非該当。現在全26/実四100で再試験。 |
| 1737/1488 | c06/9154v2原4f5c3cdc95cf46316121d7d95e3ab4fbb5779805337a71aacbbf01133f45fa6d正常六0→9156v2原bbcd8aa235bc2a2d37e064a123d15e7ef2fb79029009107af701a4ef08415283のXML26/FES0だがCLI1。新selector26にcopy元launcher終端44×四比較が残存 | 元helper SHA5d7bff94c346a1fb8def78ad4e0a020881a5a072185ffc82b2f0fb375891132fを不変保存。新helperV2四比較26とdriverのCOUNTS/selectorを事前一致検証、9160が旧44と一counter25のmetadata反例拒否。worker旧helperは元44と一致し非該当。c06/9156v3原fbac2c9e32c25e7532f228cf57f432abb3fb67d8212f86bfedafc505243d6004が26FES0/CLI0、旧normal再演0。現在cb/hostv4も同新helperで資格。 |
| 1738/1489 | c06/9155v3原d23eea68095a497be8e44ada64f3f6fd03d5b45a998aff17d1cbeb6bc97de638 raw1/PMD5-CS0-SB0、metrics fieldとgetter同名一件は適用違反 | cb91bc2ec0ef5a36652369aff5c86fa037801ccaでfieldだけmetricContextへrename、公開getter/Unit期待は不変。9160が初期Mainとの差は五field参照renameだけと実証。三role monitoring113ファイル検索で他候補はMonitoringModePolicyのprimitive enum値三つのみ、borrowed resource ownerの保持問題と非同種（その全class静的合格を今回推定0）。新PMD4に命名指摘0、当26/全一Main四100/CS-SB0/traceで再資格。 |

工具修正途中の9156driver v3 SHAa7e31fa6f3df2fba26c7e4d61644d85f2e72f5307988ef5a73a17f6b837a19efは二重escapeした件数regexが新26を不検出して子開始前1、元tool保存→v4で空白除去/四counter tokenを直接検証（実SLOTはhostv3）。9155staticv2 SHA90abbc0c728d16ee0fec448559424fcb314f51bc63d3986a80711896dd81850aはhost raw exit1 gateで子開始前1/SLOT未作成、製品静的実行0。これらの原実行時刻は未保存nullで、後から補填しない。新工具versionと元失敗は保全し、製品Testへ加算しない。9155初版/v2は静的子UNRUN、v3/v4だけ実解析。

上記全3件・全対象/非該当/再発防止まで当scope 2026-10-25 CLOSED。工具修正commitは本1869保存commit、元台帳の修正前OPEN行は履歴保持。normal三source各一回/全六0、selected四run=104実行（ca26F1/c06工具終端1/c06終端0/cb終端0）でも新Test IDは26だけ。旧成功を新sourceへ算術加算0、代替PT/実測coverageへmetadata合算0。

## 次工程・正式認定との分離

現ApiProcessLifetimeはstop/fail通知だけで既remainingを未供給、ApiManagementServerは既最大30秒入力、OwnedOutboxDispatcherは既無期限joinである。これらをAPI Unit60秒/親30分を共有した停止成功とみなさない。次は同caller経路の停止予算の供給/所有を限定し、必要な内部PG/PTと設計分類を行う。actual Main/Manager/Pool停止/native/CHR/全source四100・451/全trace/G07未分類8379/QA051finalは未受入HOLD。

技術累計838新ID/41Main/config静的5（異sourceの部品測定）と正式1964PT/53scope・原190新受入0・工数nullを分離。受入や全工程完了へ推定しない。通常報告/commit/push/PMO返信待ちで停止せず、許可された同経路PG/PTへ継続する。
