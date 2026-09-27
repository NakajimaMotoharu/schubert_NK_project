# 158 BUG291/YKT224 共有version影響再試験

018156/SS343 §11.1/SSC096、PT-OPS-BOMPROFILE-010。source f8d8dedc3のGA版重複を修正前起票し、独立literalに「正規shared版を残したまま別版GAV/file追加」の反例を実装。04:30:36 JST exit1、Storage8＋Profile16の24PT中1failure（期待IOException、実無throw）、初回bootstrap反例で停止。RED manifestはfailed XML/当時test hash/log hashだけを保存し、残反例・report/static未実行を合格にしない。

依存coordinateからgroup/artifactを取り出し全manifestで版一意を要求する4行の修正後、04:32:00 JST exit0、関連40 PT/F-E-S0/static0。3共有＋一般GA別版の反例を同method内で実到達、共有同GAVの同size/hash/複数role正常期待は維持。Profile3 concrete class line245/method29/class3/branch102・全6counter missed0。個別source hash/4JUnit/coverage/static/loghash/commandは `evidence/provisional/BUG291-GREEN/manifest.json`、REDは`BUG291-RED/manifest.json`。

YKT224の全GA検索は当該1loopを共通対象とし、別GAと同GAV同byteの各roleは正規ケースで非該当。同GA shadowの直接修正は済み。実tree深いlib/ZIP sharedclass shadow/Class-Pathの拒否は018156のfull入口で未実装、これを検索だけで横展開完了にしない。状態は直接限定再試験済・fullBOM結線/横断回帰待ち。新sourceを旧full2201と同source合格へ合成せず、PGPT/R2/R3正式進捗を増やさない。
