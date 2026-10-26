# 2078 期待値constructor128箇所・原式hash独立照合結果

2026-10-26、G03.01、群2414（開始0.5/2/5週次枠pp、cap10）。source `6612747b7a5492e5c49647d85cfc2dcbe6d75c9f`、正常compile PG10508 `bc2c2ee9ff267ab6ea56f33df42b0272636cd928c23cdb3cc9b33bf1db3773c5`。Main変更なし。原PG10252の789source構文inventoryのうち、四型を期待式に含み現在SHAが同じ128箇所/21sourceだけを対象とする。件数は構文箇所でありPT件数ではない。既原八enum Testは対象外。

## 原本・独立確認

- 原AST manifest `745d934fbb1860218efc7b5bbdbffd36d8cc9985b26a911a59ca7d50c253c72f`。元path/method/期待式line/式byte hash/source hashを保持した。
- PG10520 V3 manifest `de115abc7337ea95939b3fc80360882f250b5d3b977596b179c815a6590afa23`、actual0。元式byte hashを全128照合、source SHAを当正常compile入力と照合。四型component再代入拒否四反例、期待式誤行/誤hashの単行・複数行四反例。
- PG10522独立post `7f8c51ea963470e54006b0531d6d2363639876c574ea562748f7ba9422a83565`、actual0。主工具のlexer/括弧stackを使わず、元AST式hashと生source部分文字列の一意一致を全128確認。全元metadata field・21source不変、別の誤行/誤hash二反例。
- 実commandは `env PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg10520_constructor_carrier_review_v3.py`、同10522。各工具は前置pyflakes終了0を確認した。Python source/公開metadataのみ、Java/helper/製品/fixtureの実行・compile・classload・外部操作は全0。

## 確認できた範囲と未確認

四型はCleanupCounts79、PagedResponseData26、OutboxDispatchReport15、BatchStepResult8箇所。各compact constructorは非負/範囲/相関/nonnull等の検証のみでcomponent再代入なし。CleanupCountsの件数差、Outboxのint合計long化、PagedResponseDataのunsigned range、BatchStepResultのReason.allowsは入力の妥当性を検査し、expectedをencode/normalize/処理結果から生成しない。`fields()`/`from()`等の別処理をconstructorと混同しない。関連RD/UI/SS/TestIDは各対象class headerと元source path/methodを維持する。

100式は四型と明示literal/enumだけの引数。残28式は変数名の由来を個別確認するまで保留（JDK Long.MAX_VALUE等を含むので、28件を直ちに障害と断定もしない）。このうち五式はInspectionSummaryも含み、主結果の四型契約だけで全式の独立性を認定しない。四型単独123/混在五を区別する。

追加の読取で次を確認したが、全呼出元・fixture・要求後条件を閉じた判定ではないため、主manifestのvariable28未解決を変更しない。

|箇所|確認した引数の由来|残確認|
|LogSqlContract五|Test-local PAGE_SIZE=100|各Test/SQL後条件とoracle適用性|
|LogQueryRepository.adm055|固定total配列、JDK max/minと100件paging式|seed/要求境界の完全性|
|UserQueryRepository.assertPage|呼出三箇所、固定値又はcount/requestedのJDK算術|helper全呼出元/期待wireの要求join|
|InspectionAttemptのLong三、LogCleanupValue一、StepCleanupService一|JDK Long.MAX_VALUE固定境界|期待条件と対象演算の独立根拠|
|StepCleanupService二/CleanupStepRepository三|Test-local固定delta/total配列、index演算|fixtureの件数根拠/7kind対応|
|CleanupStepValues二/InspectionAttempt並行二|0..63のloop index、入力indexの独立算術|実測の並行結果は今回未実行|
|InspectionAttempt.matchingSuccess|入力InspectionSummaryのcountsからcodeを選ぶ|入力carrierの契約と期待値相関|
|InspectionSummary混在五|同record compact constructorはnonnull検証だけ、固定counts/BatchRun又はInstant.parse literal|run/inputの全由来・DB期待値対応|
|MorningExpirySession一|currentで期待結果を分岐|current/clock供給と業務観測の因果を未確認|

## 工具障害・横展開

BUG1839/YKT1590を修正前起票。原10518はAST期待式lineをassertion行と解釈し複数行でactual1/OUTなし。V2/10519はline/hashを是正したが混在constructor五を全四型限定guardで拒否しactual1/OUTなし。両原工具を保存し、V3だけが真正actual0。失敗をPT失敗・安全拒否・製品障害に変換しない。元群開始見積は不変更、tool手戻りを元計画消化と分ける。

## 受入・保全

STATIC_SOURCE_REVIEW_PARTIAL_WITH_ARGUMENT_PROVENANCE_PENDING。新PT0、coverage未測定、whole G03/451未受入、新個別受入0、正式1964PT/53scope・個別17/190・工数null・QA051final保留不変。旧source実績を合算しない。Graph9/Root/実DB/VM/key/permit/intent/未特定操作のHOLD維持。鍵witness二fileは未読取・未実行・未push。次は未確認28式のうち独立して読取できる入力由来・原要求/TestID対応を限定確認し、実際のencoder依存があれば修正前起票してPG/PTへ進む。
