# BUG-154 group record終端LFの独立負例

先行c07883c3。2026-09-12 22:30:45 JST、探索1はStorage58/Batch99＝157 PT成功だがgroup parser line91の終端LF false1分岐が未網羅でcoverage gate失敗。最短正常record13byteからLFを除くと12byteとなり、最小長guardで先に拒否された。raw log SHA256 cfdad27510552d6f5b2dc5c5746673bbad775a0cb008fbc63a8a20a4b822de3f。

GID002へ13byte以上の`schubert:x:2000:member`（LFなし）を追加して終端guard自体を検証する。最小長・多行・CRLF・全制御・prefix/colon/GIDの各既存負例も維持し、Productionの判定は変えない。CFG/ENV/EFILE等の既存parserには同じ変更がなく、正式04の全分岐成功へ追跡するためYKT追加なし。今回PG155のNS結線・正式全reactor/35scope成功後に完了認定する。

探索2は22:33:47 JSTに157 PT/coverage成功。NS追加後の探索は22:43:06 JSTにStorage58+Batch107＝165 PT/coverage4指標100%/静的解析成功。全体正式試験前のため、障害状態は再試験待ちを維持する。
