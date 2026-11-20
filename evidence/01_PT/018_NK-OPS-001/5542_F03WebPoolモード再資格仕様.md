# WebDbPoolMetricRecorderモードの再資格

WBS-F03/2-2、P018-09、UI252、SS351 §8、451、BUG-3440、YKT-2751。元仕様1728 WEBPOOLMET001～008を、一回で同candidateに再資格する。合成SimpleMeterRegistryと明示値のみ。実pool・DB・通信・サービスは使わない。

DEBUGは規定4series、STANDARDは登録0、未知は元CONFIG_INVALID、nullは元境界拒否。正常、空、欠落・0、長整数、null、横断並行、借用registry部分失敗と上限を元の独立期待で確認する。公開ABI、static・typed実測、本体および二ネストの生counter、該当する実行結果・時刻・SHAをPG40994のmanifestに保存。保持されたPG15060／PG40992の加算は行わない。
