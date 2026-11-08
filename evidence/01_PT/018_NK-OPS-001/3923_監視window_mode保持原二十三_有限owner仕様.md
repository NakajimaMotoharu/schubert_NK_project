# 監視window・mode/保持：原23試験の有限owner是正

G03.05主/P01809関連追加0、REWORK原1/4/8共有pp cap10。原ContinuousConditionWindowTest8/MonitoringModePolicyTest7/MonitoringRetentionConfigurationTest8のwhole三Classを保持。元1561/1541/1700・必要scope2803を参照し、現在Main二Source全五physical（Window/State、Mode/DetailService/RetentionConfiguration）を分母にする。Retention八は同Mode Sourceの必須分岐であり除外しない。helper AlertThresholds/AlertLifecycle.Severityは部分参照で再受入なし。Main全本文/initializerと全Test bodyを確認、純粋Duration/Map/enum/公開hashのみで実collector/clock/retention削除/service/FD/DB/JMS/VM/Root/FFM/credential/key操作0。

BUG2566/YKT2177へ修正前起票。Windowは内finally.shutdownNow/await10の外にTWRが残り、await未達assert後にも無期限closeが走る。外TWRだけを取り除き単一finally所有へする。ModeとRetentionのinvokeAllを10秒二箇所へ、Retention TWR ownerをfinally.shutdownNow/await10へ（owner是正二、入口二）。AlertRegistryは既にtimedinvokeAll/非TWR/finally await10であり同因非該当・元成功は再演しない。

固定0/299.999999999/300秒・NORMAL/UNKNOWN/gap/max/nano/逆行不変、32mode真理値・15日/decimal5GB/0・欠落/null/片側1/GiB/最大・固定hash/text・各64並行の元23期待を変更しない。新Test/fixture抽出/代替0。Source変更前はGit object/hashだけ保存し、全bodyの許可差分逆復元/field内容を照合する。

現normal22084/静的22086・現Consoleプロフィールを利用。format→PMD/CS全指摘個別適用性/厳密lint先行→最小batch/protocol/JSpecify/Console/JaCoCo/JDKと全source/class/SDK事前確認→source固定push→testだけcompile/元whole23を一session一回/外側180秒→全5Code/Source二のcounter/実CRC/四heldinit0/全XML23/独立literal・goldenの別照合。新source・coverage100は実測してから判断し、欠落branchやgenerated/natural0を偽100化しない。元55/既成功/source旧execの再演合算0。全YKT2177/正式1964-53・unique520/候補114pending12whole93暫定/工数null/QA051/全HOLDを維持する。
