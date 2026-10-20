# 1222 protocol表現是正：実行結果

1220/PG-D443/BUG1498/YKT1258。Source **86287c3fb83b483050b88dce04bc644961682bc4**、dev-foundation。PG5844/元36548は2026-10-20 **03:38:01.942395Z～03:40:10.536197Z**、phase0,0/真正0、**105件/26suite（protocol全96/20＋guard九）、F/E/S/flaky/rerun/not-run0、六format/型nullSpotBugs0**。archive **c7eac842b34ade027329af58c657f344d6d2c9c1c70b9c176cbdfc28beb8c4d4**。新case追加0、原Test/oracle/resource/POM/Current baseline不変更、JDK25.0.4/Maven3.9.12/JaCoCo0.8.15・Linux/offline/通常user、実VM/Unit/原本/鍵/permit/failed-cohort不操作。

六修正型は **L366/M55/C6/B203全miss0**。boolean幅/正数下限・区分値の幅・version001・八column/field start/length、zero-read後store/offset増加を、独立byte/TSV/JCAと正常/境界/null/未知/EOF/IOの既96で検査した。命名定数だけを読んだ水増しtestやproduction由来expectedは追加していない。

PG5848/元83089独立実0、全851source/1666実Mainを照合し、宣言六ownerのouter六＋`LayoutFieldCatalog$1/$MutableFields`の計八物理差（nested/debug含む）だけ、**残1658全byte一致**。六file全文が事前の定数命名/offset分離の宣言変換だけ、既public ABIの追加/削除/変更0。PMD無除外で**条件literal七＋operand increment一が実コードから消え、raw1594→1586**、他rule件数は維持、processing0/Checkstyle0。公開manifest **3c2ce6616b6b050543ec7ab9e580f2f2890d8bbf58fc7597da35a913c2f24100**、raw inventory **dd25ce1a61a9c3136f0cdce90d1689f084463ecc962fabfb763504f69c61c0d8**。rule/抑制/coverage除外の変更0、F03全体未受入。

PG5850独立artifact読取実0は全105の源Test/XML集合・各casePASS・六型実counter・全851source/1666byteを再突合。公開`evidence/provisional/PG5850-protocol-expression105-v1/manifest.json` **51df505573725374877f0395a85e7ce53e11e20743bb1f9f5ad62baaa79921b5**。各EXPR観点の実methodは1220と同じclass/method/XML hashで追跡し、共通caseを重複加算しない。新PG/PTの当八表現scopeを完了、修正86287c3fb、完了2026-10-20。実global/Native/CHRや旧3967sourceの成果とは分離する。

## Protocol moduleの実測全counterと17非実行classの根拠

当96/20でmodule XMLを独立読取し、**LINE3480/3480・METHOD743/743・CLASS159/159・BRANCH1014/1014**、INSTRUCTION17441/17441/COMPLEXITY1277/1277を確認。XML SHA **0a57147001af15dc2b6b2e1983ba255fefb164ac9ffab7ca577034edb58ec48d**、追加のPT再演0。物理class176との差17も`javap -v -p`（読取専用/Production method実行0）で全件照合した。

- compiler生成switch-map四：PayloadCodec$1、MediaDescriptorValidator$1、FieldDefinition$1、LayoutFieldCatalog$1。全てACC_SYNTHETIC、実XMLでcounter非生成。業務switch自身のbranchを削らず上記実counterへ含む。
- annotation package-info七：codec/file/header/layout/layout.semantic/time/transport。全てACC_INTERFACE/ACC_ABSTRACT/ACC_SYNTHETICでCode無し。
- abstract interface六：FieldValue/LayoutPayload/PayloadData/PayloadRecord/ProtocolId/WireEnum。全てACC_PUBLIC/ACC_INTERFACE/ACC_ABSTRACTでCode無し、実装側の実行bodyを測定する。

対象とflag/Code有無・実counterは同公開directoryの`protocol-module-coverage.json`へ保存。設定を追加して除外したものではなく、既固定JaCoCo出力と実binaryの母数を説明した。176/176と水増しせず159/159と物理176を区別する。ad-hoc metadata読取のraw stdout file/正確な開始時刻は欠測nullを明記し、coverage XML/元source/archiveは保持する。

PG5852実0は旧482の**全source/全座標/全owner実byteが一致**した分だけ現862へ再認証、保留0・新review0、**pending482/未review1104/raw1586**。公開manifest **6eff7b7aade5f9770d70cdb294a3b37f4731fd479088ee40f7f945942c3e1d0a**/inventory **7a0d1352e71e99bb76f2743b95d6a89938a96ab0008c212d9ba6986ec8a83e44**、旧3967 PASS/current whole参照は未移植、同Main PMD再演0。global品質/trace・必要全scope同source/run・当source native/CHR/QA051final/引継ぎ等は未完。正式1964/53・17/190・工数率nullは不変更、PGPT又はIT/ST完了ではない。
