# F03 正式SpotBugs対象完全性

NK-OPS-001、WBS-F03/2-2-b、SS354・451第3節、006の製品六module共通。PT-OPS-F03-STATIC001は固定したGame相当のroot／innerの二型と別拡張子から期待class集合を独立に固定。002はMissingClass／分析Error、属性省略、明細、Bug、summary欠落を拒否。003は対象数が同じでも異なるclass、class欠落・重複、報告total不一致を拒否する。実装はコンパイル済みMainの全物理パスとClassStatsを集合にして照合する。

PG42816、dev-foundation、対象commit a8d94c1e87。Python3.14.4の工具119件成功。PG42762の既存Protocolの実compiled物理176、正規JARのclass byte176、元SpotBugs ClassStats176が一致し、MissingClass、Error、Bugいずれも0。元XMLから合成したMissingClass=1の旧受入／新拒否を確認した。原証跡、コマンド、時刻、終了は [PG42816 manifest](evidence/PG42816-formal-spotbugs-completeness-v1/manifest.json)。新しい解析起動と製品PTは0、六製品への正式適用は当sourceの収録条件が揃った時に判定する。BUG-3625／YKT-2850の工具範囲を完了。
