# PG581 現source追加八native採取・counter

Program NK-OPS-001、関連SS343/353/354・451、Production 969d8ded10c0bf5841d9e3a5c531e922caf4a24a、operator 462cf7cd5fd5549fb4e07ca581c9bf1e47af3e52。
Test PT-OPS-PG581-001: PG579八streamを各Unit起動/終了monotonicと真PID1 realtime offsetの独立窓、single-session、PG580後の固定hash/九metadataで採取する。旧五history/別source/PG541565 selectedを混用しない。期待=各NoMatch0、旧十currentとの差が非負、原値/サービス不変更。Test002=atimeのみ変化許容・九属性各変異拒否、Test003=実after七key schemaと使用三key整合。独立Python metadata/schema2fixture成功、Pyflakes/差分検査0。

実command python3 -B tools/quality/vm/050_s1/pg581_native_counter.py、JDK25.0.4/JaCoCo0.8.15/ASM9.10.1/Linux host・Ubuntu26.04 VM。v1 exit1 stat_result atime、v2 exit1未存在nativeキー、BUG867868/YKT636637修正前登録、両旧失敗はtool output履歴に保持・合格へ加算0。v3 exit0/2026-10-08 17:42JST、新八＋封印十=18current streams、六module classByteMismatch0。追加44line/4method/0class/10branch、未網羅1032/197/12/887。全coverage100/正式scope受入ではない。

私有PG379/pg581-current-eighteen-native-v3/manifest.safe.json SHA f7824086cf30e00f246deeb9cf5c3456a1408b34032a0f4f44a7a3151032f5c8。immutable私有record内runラベルv2は記述誤記として開示、実directory/source/hashからv3を識別し原記録を上書きしない。公開manifestにmodule四counterとgain、raw/session値は含めない。BUG867868当工具範囲限定再試験成功、全PGPT/旧BUG850/QA051は未完。
