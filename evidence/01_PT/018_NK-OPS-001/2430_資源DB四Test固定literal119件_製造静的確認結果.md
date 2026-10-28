# 2430 資源・DB四Test固定literal119件・製造静的確認結果

2429・PG-D781/782、source6d7f55c22a3ffec8a9013e706282ac845c595492（四Test private String119のみ、Main不変更/未配備）。新TestID/新physical0、Product PT0・動的NOT_EXECUTED_HOLD・coverage NOT_MEASURED。原静的217rawから119だけ除去、他98を保持しPMD自身4/rawgate1、Checkstyle0。全source token逆と131非同値反例、全1843Main同byte・旧Test1974 keyset不変/当四SourceFile16class内14変化・他1960同byte・新0、追加private119 ConstantValue以外の全method/private/public metadata不変を独立確認した。

## 公開証跡（全てevidence/provisional/配下）

|元run/session|manifest SHA256・結果|
|---|---|
|PG13204-resource-db-literal-v1 原本|a8cb7fe67793a319a5f1d0fdd91fd527d1dcffd28452dc7bcf6cd6d859473e0c /0|
|PG13206/session21309 元static比較|工具真正1、PMD4/CS0保存、OUT未作成・BUG2037|
|PG13207-resource-db-literal-preflight-recovery-v1 /49693|abcff1ed823336314e9f56f1f66cde531a44c6e954d14830738fd511733d4b22 /0・元解析再演0|
|PG13208-resource-db-literal-v1 /80260 六normal|01df6a3463d330c92815ca7ac11dd27d4eb320d767ee8069ef36898c6506ecd4 /0・PT0|
|PG13210/session63482 元六static|Maven0だが18 MissingClassの後条件で工具1、OUT未作成・BUG2038|
|PG13211 元CLI計画|依存version guard1・CLI未実行・BUG2039|
|PG13213/session70160 CLI計画v2|help実1/工具1・begin全hash保存・解析未実行・BUG2040|
|PG13218-spotbugs-fresh-aux-plan-recovery-v1|a60a6ff0579588e9a10b5a2de6b2d2f4587f983408645a87e8cd4c7ad6917564 /0・旧help1保持/再演0|
|PG13216-spotbugs-fresh-six-cli-v1 /62011|3ec8326e0c54daf26b3bc500a7b2ceb62f34abc0a9647c8ed140e9f19708f8c0 /0・当source六全解析|
|PG13212-resource-db-literal-v1 /26511 全物理/119定数|f0a0817f4a3cbac3d4ebacc267e892b09510c9994cf31daf6c3e1e20821f3a65 /0|
|PG13220-spotbugs-fresh-aux-post-v1 独立解析確認|2ac356e6962abdf7208277da575a6213b924809b1d0f09cc80e8f16243454e3b /0・8反例|
|PG13214-resource-db-literal-v1 /57199 第一entry trace|e9968ca1718adb93ecb662552270f754a254ebe801487117789d5941bbf978b6 /0|
|PG13215-resource-db-literal-v1 /57199 第二entry trace独立|bbbda258354ff88e9bbe9a385d36d89bbc868036be25a9098281e08be1d904cd /0・8反例|

## 追加発見と是正・再発防止

BUG2037/YKT1785：元診断はcomma行位置/一空白、元XMLは新comma行位置/既知二空白という表示差だった。別厳密比較で同じliteral・出現数・rule/class/methodと原98rawを照合、位置/空白対以外を同値化しない。元failed stageのsource hashは永続記録がなかった事実を保持し、連続してsourceを変えなかった操作履歴・現全文逆/元report行anchorで回収した。過去hash観測を捏造しない。七非同値format反例と元解析出力/exitを保存し、元PMD/CSの再演はしなかった。

BUG2038/YKT1786：Maven auxがlocal repository内の古い同座標snapshotを参照した。API5/batch6/bootstrap3/Web4の延べ18 missing（固有8class）、protocol/storage0。現sourceのJARに全対象が存在し、古いproject aux JARには存在しないことを個別に照合した。既SpotBugs4.10.4/Max/Lowと同runtime（plugin POMのcommons-io管理2.22.0、SLF4J2.0.18/Log4j bridge2.26.1・core明示除外を含む）を固定し、tool CPと解析aux CPを分離、auxはfresh sibling六JAR＋固定外部依存だけとした。old m2/元報告/失敗工具は不変更、標準gateや閾値を緩めていない。

新13216ではAPI467/batch645/bootstrap117/protocol176/storage80/Web358＝全1843のClassStats集合と物理JAR集合が完全一致。BugInstance/MissingClass/解析Error各0、六真正0、入力hash/原未解決18→当0を独立13220で確認し、解析再実行なしの八反例も通過。これは当sourceの静的解析だけで、旧source/動的native/PT/coverageの認定には転用しない。従来Maven経路をそのままactive判定に使わず、以後もfresh依存/完全分母/Errorを必須とする。

BUG2039/2040-YKT1787/1788：CLI計画のruntime座標仮定とhelp終了0仮定をそれぞれ修正前起票。元2.21未導入guard1とhelp1を保持し、別metadata回収で既plugin managed2.22/元help全optionを確認した。追加インストール/モデル変更/権限変更なし、旧help再演0、metadata0を解析PASSへ換算せず実解析13216を別記録した。工具手戻り（2037/39/40）と、追加発見した旧解析完全性不足2038を原119是正から分離する。

## WBS・状態・費用

995registryの四SHAだけ変更、他991row/全canonical owner-cost/旧runtime/unknown二/原論理941歴史943/原見積不変。raw8319=Main1502+Test6817、累計原是正1106、用途参照3271・current-source pending1024（既参照48の当source再照合を追加保留）・参照なし5048。全体違反件数null、全WBS audit1/HOLD、全F03/451/正式受入は0増分。元1964PT/53scope・歴史17/190・工数率null/QA051final保留を維持。BUG2036/YKT1784は全119のPG/静的確認済だが動的再試験HOLDで全面完了日なし。工具2037～2040は当新解析/独立postまでの限定完了、旧品質結果の上書き・将来工具無欠陥保証ではない。

群2796開始の原2/5/9pp・cap10を変更せず、共有6→7（同reset1793774153・他chat込み）を観測、専有費/N/Tnull。原計画119是正、追加発見1（旧解析missing18）、工具手戻り3、event書込前leaf型guardのcommand手戻り1、bind前unused import等authoring2、追加source再資格cycle0を分離。P00403主・P00901構成/追加費0、P01702はsplit親のartifact参照だけで推測の子配賦をしない。次点検used10、残10以下/不明停止。最新save/push/cursor/次作業は456、通常小群で停止しない。
