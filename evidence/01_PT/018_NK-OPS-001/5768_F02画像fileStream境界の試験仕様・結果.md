# F02 画像ストリームのfile所有境界

NK-OPS-001、WBS-F02-a、SYS-005、SS311 §3／§5.2、BUG-3662／YKT-2879。

| Test ID | 独立期待 |
| --- | --- |
| PT-F02-FILECALL018～020 | Web Controller、API listener、Protocolにおける直接Fileとファイルcacheの入出力4型を所属規則で各4件検出する。 |
| PT-F02-FILECALL021～023 | 上記三所属の借用メモリcache入出力2型は今回のfile所有規則で0件。 |
| PT-F02-FILECALL024 | Batchの所有adapterで直接File・ファイルcacheの入出力4型は今回の所属規則で0件。 |

固定合成fixtureはcompileとArchUnit class inspectionのみ。メソッドや画像ファイル処理を呼び出さない。JDK25の各型の取得先とcache媒体に基づき、期待を対象工具から独立して固定した。
[Java Image I/O Stream API](https://docs.oracle.com/en/java/javase/25/docs/api/java.desktop/javax/imageio/stream/package-summary.html)

JDK25の実行commandは repository root の `python3 -B evidence/01_PT/018_NK-OPS-001/input/5768_f02_image_stream_ownership.py <new-output> <baseline|regression|protocol>`。source、時刻、監査exit、生出力のSHA-256は公開manifest参照。旧工具は12件見逃し。新工具は既60＋新7合成ケース、期待指摘44と一致。監査exit 1は意図した合成違反、外側の比較exit 0。正規Protocol 176と合成anchor 5の監査はexit 0・指摘0。初回Protocol起動前のfixture組立assertは修正し、実監査を一度実施した。F02正式未受入、製品PTと製品coverageの加算0。

[公開manifest](evidence/PG43076-f02-file-backed-image-stream-boundary-v1/manifest.json) SHA-256 `60b245bf61e6c9654e6d5a1c6279955c8477b3d78584c0c899ab1e6b4fd5b7be`。
