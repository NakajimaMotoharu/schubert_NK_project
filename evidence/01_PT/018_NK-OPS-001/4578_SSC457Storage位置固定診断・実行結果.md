# SSC-457 Storage位置固定診断の実行結果

Core 280d6181d166eefc48adcfecda24df36bd4f3c95、Run source 33d49561f48344c45f56ae19fb560b36409fe79a。PG38490の初回は元5＋新規PT-OPS-CREDLOC-006、全6成功、真正終了0、F/E/S/未実行0。PG38492の独立XML、物理2（自然NoCode 1）、実行CRCを照合。PG38498の未フィルタは99命令、26分岐、24行、5メソッド、1クラスの全到達。公開ABIは同一。厳密型、固定文、causeなし、suppressed 0を確認した。

PG38484/86の厳格コンパイル、Checkstyle、format、SpotBugsを確認。PMD生5は旧PT-005の専用workerの所有、finally中断、有界終了を各箇所に照合し、適用指摘0。独立読取の初回はTSV列の解釈を誤り、保存した元rawから再解析した。計測とJUnitの再起動0。BUG-3227、YKT-2676。実環境・元項目P003-07全体・全451は未成立。証跡 evidence/01_PT/018_NK-OPS-001/evidence/PG38498-p00307-credential-location-fixed-diagnostic-independent-v1/manifest.json SHA256 1a3af9f31edc3425025c892cd69c0b0e0bf77357d04286c32faffdb27e2f8309。
