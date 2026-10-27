# 2185 Batch標準source owner例外保全PGPT仕様

NK-OPS-001/WBS-F03、BATCH_STANDARD_SOURCE_GUARD_PGPT_V1、事前1/4/8共有pp cap10・使用32/reset1793599188。BUG1908/YKT1659/PG-D702、RD171/UI252/SS311351/411/1810・2183/2184。元source d431/11312/11314の静的反例を修正前根拠とし、元107成功を失敗へ変換しない。

対象BatchStandardMetricSourceTestの14owner（001/003/004/006..016）、原16method/全独立入力・assertion/例外identity・明示close/失敗retry・GC→registry順・借用条件を保持、追加外側finallyで取得直後からcleanupを試行する。016executorはTWR、元release/shutdownNow/await10秒とFuture/latch10秒を保持。ownerはplain try/finallyでTWR内早期close規約を迂回しない。Main・期待値・既冪等契約変更0。

F03-BATCHGUARD001：原14methodをsource/actual資源指摘から選択、各owner宣言後にguard・末尾finally、016TWRだけ追加。元全tokenへ独立逆復元、各guard欠落/誤owner・Test無効・executor TWR欠落/期限変更をmetadata反例で拒否、他全input/Main不変。cleanup例外をPASSへ正常化しない。

002：固定source正常六module package/Enforcer/format/NullAway/Werror（PT0）→元BATCHHOST001..016だけ閉catalog専用日本語JVMで通常実行。固定factory/ProbeRegistry/ProbeGc・default own-JVM public MXBeans/owner保持GCのみ、強制GC/外部process/VM/Root/DB/鍵/ネットワーク0、元2worker・latch/Future10秒/外側240秒・own空CWD前後不変、自動探索無効。全16期待は1810と元各literal/count/order/identity・独立Runtime CPU値から作成しProduction出力から生成しない。

003：当一Test実PMD/CS/processing・元23rawからの実変化、残2ProbeGcのcomposite所有依存をMain ack/closeとguardへ照合しraw保持/未分類を自動0化しない。同一exec/session/CRCで完全Batch645/SourceMain四counter・Main1843/他Test物理byte/当一SourceFile差を確認、未達は未達・旧exec合算/除外0。

004：元owner/cost・全歴史/原941943/予算/acceptance・所定WBS audit真正結果を保持し、source/command/env/時刻/exit/XML/counter/BUG/hashを2186へ束縛。BUG1908再試験/横展開は当範囲証拠が揃ってから限定完了。正式1964-53/17-190/工数null/QA051final/全安全HOLD不変、通常群/commit/報告で停止しない。
