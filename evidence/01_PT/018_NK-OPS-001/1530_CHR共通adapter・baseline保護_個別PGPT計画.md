# 1530 CHR共通adapter・baseline保護 個別PGPT計画

2026-10-23、WBS-P020-01.01。初回九受入/C03受入後の独立一群。参考.5/1.33/3pp、共有群上限10ppを着手前event1779へ固定。source e7d64fda2453e906ee6ccc5fe718e5c29841e4aa、終了依存F02は490で同source受入済み。

## 範囲と安全判定

SS355§4/§12のCurrent/NK共通TargetAdapterとbaseline不可変guardを対象とする。親共通四Mainのbuild/品質は共有証拠として一度だけ測定するが、比較/DIFや全G01～06の子02/03、実NK/Browser/Current captureは本群の新規受入へ加算しない。旧020の57f9ac2/41件は現在の四Main/Test/POMとbyte差があるため歴史証拠として保全し、現在sourceへ移植しない。元Production六module4222成功の再実行ではない。

既5host suite `ArtifactComparatorTest,GateCliTest,GateContractTest,GateContractValidatorNegativeTest,TargetAdapterTest`を固定選択し、CurrentCharacterizationTest/Native関連/SharedLog driverは実行しない。Maven offline、Java25、固定e7 archiveの新作業root/target/TempDirだけを使用。全Main/Test/fixture/POMの入力hash、元baseline/currentの全file hashを前後に照合する。既target/旧logの上書き・actual VM/SSH/HTTP/DB/サービス・Current master・実credential読取なし。

着手前にMain四classにprocess/network実行がないこと、選択TestがURI文字列だけを評価し、current/credential/pgsocket等は新fixture内で作る非秘密dummyであることを確認した。GateCliTestの昇格先・負値・0600 permission操作は新TempDirのみ、原baselineは読取/copyだけ。固定sourceへ工具やassertを注入しない。F03 Root11/実環境HOLDの試し実行ではなく、明確な許可済み共通harness PTである。

## 個別PG・独立期待値

| 対象 | 正本／独立oracle・Test method | 確認する後条件 |
|---|---|---|
| Current/NK共通入力 | TargetAdapter.create/Target.parse、TargetAdapterTest三method。SS355のHTTPS/allowlist/23Current＋N01metadata/24NK、fixed catalogと明示URL/path値 | null/空/未知target/host要素null/未知host/不正scheme/userinfo/query/fragment/path・既出力/外側path/symlinkを拒否。呼出しで実接続なし |
| case/run出力 | caseArtifact/executableCaseIds/endpoint、同三method。24ID/N01だけNK_ONLYをfixture側で固定し、重複/余剰/欠落/未知適用値を負確認 | immutable copy、同origin絶対path、固定case artifact先。空/未知ID/NPE正常化なし |
| baseline不変 | GateCliTest.baselinePromotionIsImmutableCommitBoundAndSymlinkSafe、固定source fixtureからTempDirへ昇格、短/40桁commit値・24case/2screenshotの明示期待値 | 既存nonemptyへの再昇格拒否、誤commit/入力symlink拒否。原baseline hash前後一致。fixture内の既存empty先は仕様上の未作成内容であり原baseline書換えではない |
| 原子出力/競合 | GateCliTest.atomicJsonWriterRejectsConcurrentUseOfTheSameOutput、手動barrier/固定first JSON | 同じoutputへの2回目拒否、first完了後JSON完全/part残置0/null出力拒否 |
| source固定 | GateCliTest.verifySourceAcceptsIndependentInventoryAndRejectsDriftAndSymlink | 新fixtureの五source/一document/二masterを独立hash規則で算出、drift/symlink拒否。実Current原本へのアクセスなし |

親他二Mainの補助suiteは全current物理class/four counter/正常・異常・nullの品質を観測するために含める。期待値は各Test側の固定JSON/literal/独立hashであり、同Production methodでexpectedを生成しない。PGは上記TargetAdapter全method、GateCli dispatch/source/promotion/atomicと関連契約を読み、疑義が出た場合は修正前BUG/YKT、必要上位台帳へ先行起票する。

## 実行・判定

新only `pg6966-chr-adapter-host-v1`へarchive/command/beginを保存後に一回だけ実行する。開始/終了コードは意味検査より先に保存し、unknown/beginだけなら再起動禁止。全原XMLのF/E/S/flaky/notrun、実counter（N/Aを100補完しない）、全四Main/class/Test/fixturehash、lint/null/static/format適用性とbaseline後条件を照合する。coverageやqualityが未達ならchildは未受入で保存し、予算を理由に合格化しない。

正式1964/53・歴史17・QA051final/PTALT0・工数null・全actualHOLD維持。本群の新PTは共通harnessの限定host PTであり、Production六module4222や実CHR case/旧nativeに加算しない。子01を閉じるまで無関係なWIPを追加しない。
