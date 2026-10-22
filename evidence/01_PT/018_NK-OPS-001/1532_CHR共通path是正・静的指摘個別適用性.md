# 1532 共通path是正・静的指摘の個別適用性

2026-10-23、WBS-P020-01.01/BUG1640/YKT1393。common source **3c70db39377cee751d7ecd12bb439c447e0c61c0**、Production六moduleの資格sourceはe7d64のまま（src/POM/wrapper/旧static規則全byte差0）。この二sourceを同じ実行sourceと偽らない。旧e7の10受入/歴史17は保存し、新common受入には必要F02だけの同byte再認証を明示する。

## 実障害と独立試験

原6972/31c7d9467のMaven実1、43件中旧41成功＋新PATH001/002が期待IAEに対して実NPEで失敗。原資格6974 **909ddd0b190c4a552b88b2710e5b78e69799f82aa1aba4b65c4a2887d159b3d9**。red期待値二methodと旧41全文は固定。既存Main4/原baselineはRED時不変更、null.part残置0。sourceRun根名無しの未修正実行はfixture外IOの可能性があるため実施せず、未実施を成功REDにしない。

GateCliのlog parent/output parent/sourceRun nameを副作用前に拒否し、同二oracleを変更せずPATH003 null/root入力を追加した。修正3c70db393、原6976の真正Maven0/44件/5suite、F/E/S/flaky/notrun0、原baseline/全snapshot入力前後同一。全Mainは元四classのうちGateCli一fileだけの変更であり、codec/DDL/業務機能/Root等の変更ではない。

原6980 **0bbc80f788ac9c26caada7f363415a803aa6cef3796222d519467d6d60e34631**：独立CRC/session監査は元execを公式JaCoCo0.8.15 APIで分析し、実8classのJar/class hash一致・CRC mismatch0・単一session・counter完全一致を確認。line1087/method131/class8/branch539全miss0、旧985line/旧41や六module/nativeとのunion0。compile release25/lintWerrorとEnforcer、実対象9fileの同Spotless規則に成功。Tool compilerのNullAway適用packageはNK本体であり、このcommon packageをNullAway解析済みとは主張しない。ここでのnull静的検証はSpotBugsデータフロー＋下記全指摘reviewと独立negativeによる。

## 原rawを保持した適用性判断

原6970/e7はPMD43/Checkstyle0/SpotBugs16（実exit4/0/1）。修正後6978/3c70はPMD43/Checkstyle0/SpotBugs13（実exit4/0/1）、manifest **8a215d4584831c544d56e17c1ca4e3bf7be8851d751179d3df81d5fef1985efb**。raw非0を0へ書き換えず、ルール/閾値/入力除外/suppressionを追加しない。全findingはsource全hash・line snippet・rule/method/instance・原report hashと個別に対応する。以下は四common Mainに限った判断であり、F03のRoot11へ横流用しない。

| 原指摘種 | 対象・個別確認根拠 | 判定 |
|---|---|---|
| PMD UseConcurrentHashMap | compare/artifactFiles/verifySource/preflight/compareCurrent/report/promoteCurrent/prefixed/fileHashes等のmethodローカルMap。同期stream/同一threadで構築しJSON又はcopy結果へ渡す。共有mutable mapではない。真に共有されるACTIVE_OUTPUTSは既ConcurrentHashMapの集合で、競合barrier Testもある | CONTEXT_NOT_APPLICABLE（共有アクセスというルール前提が無い） |
| PMD AvoidDuplicateLiterals / AvoidLiteralsInIfCondition | 各行のPASS/FAIL、manifest key、DIFのmode/適用値等をSS355/固定schemaと照合。これは規約にない定数抽出/独自styleを新たに強制する根拠ではなく、承認済み外部contract literalをそのまま検査している | REQUIRED_CONTRACT（原文字列を変更・正規化しない） |
| PMD AvoidFieldNameMatchingMethodName | TargetAdapterのfinal target/baseUri/evidenceRootとTarget.propertyのgetter。同名field参照は括弧無しでmethod再帰ではなく、constructor後不変。既命名lowerCamel/enum契約を満たす | CONTEXT_NOT_APPLICABLE（実害/命名違反なし） |
| PMD AssignmentInOperand | GateCli.sha256とGateContractValidator.sha256のbuffered read。読み取った長さを同じwhile条件で終端判定し、その長さだけdigestへ反映。try-with-resourcesと独立aggregate hash Testがある | CONTEXT_NOT_APPLICABLE（意図した単一readの標準idiom、値取り違えなし） |
| PMD AvoidBranchingStatementAsLastInLoop | containsAnyの内側比較不一致はlabel付きcontinueで次の候補startへ進む。target空/長過ぎを先行拒否、正常一致/不一致/長さ境界は独立Test。通常continueへの変更は検索意味を壊す | REQUIRED_CONTRACT |
| SpotBugs NP（ArtifactComparator.artifactFilesの二行） | Files.list(root)からの直下entryで、regular file条件の後に名前を参照。filesystem root自体はlistの子ではなく、name無しPathはこの集合に入らない | FALSE_POSITIVE（標準NIO childrenの不変条件） |
| SpotBugs NP（GateCli.caseIds二行、GateContractValidator.caseIds二行） | 同じくFiles.listの直下entryで、artifact名の正規表現を評価。存在しないdirectoryは空を返し、rootそのものをentryとして扱わない。独立missing/nested/linked/catalog Testを参照 | FALSE_POSITIVE |
| SpotBugs NP（verifySource lambda、validateRun screenshot lambda各一行） | regularFilesが先にNOFOLLOW_LINKSのregular fileへ限定。directory/rootは含まれず、名前無しPathを渡す流れなし | FALSE_POSITIVE |
| SpotBugs THROWS_METHOD_THROWS_CLAUSE_BASIC_EXCEPTION五行 | compareNk/preflight/promoteCurrent/両sha256は独立CLI工具のchecked例外伝播境界。失敗を正常化せず呼出しtaskを非0へする既契約であり、Production境界で例外を握り潰す実装ではない。既APIに新しい工具styleとしてthrows列挙の限定を後付けしない。IO/JCA失敗は独立負Testで確認 | CONTEXT_NOT_APPLICABLE（共通工具の例外伝播宣言、仕様違反ではない） |
| SpotBugs NP（preflight/writeJson/promoteCurrent、旧三行） | こちらは任意入力のPathで、list/regular-fileの前提が無かった。上記の偽陽性分類を流用せずBUG1640としてguard是正し、二RED/三GREEN negative・正常/競合・元baseline不変を実証 | FIXED_BY_BUG1640、旧raw保全/当rawでは三件消失 |

全56当rawを明示6PMD rule/SpotBugs二型・許可method集合へ一意joinし、未知rule/method/残る実障害NP/parse error/抑制は拒否する。語だけで正当化せず、各source snippetと関係Testを保存する。raw checkerの違反件数が0だったとは記載しない。判断未済を受入へ加えず、子01の固有deliverable/qualityと必要終了依存が成立した時だけsource別受入する。
