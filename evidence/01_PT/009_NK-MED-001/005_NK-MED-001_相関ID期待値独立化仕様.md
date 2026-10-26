# NK-MED-001 相関ID期待値独立化仕様

## 目的と追跡

BUG1822/YKT1573、G03.01。RD FUN-005～007/AUT-001～004/PER-004～006、UI232の共通電文/Media正本UI235・237・243、SS324/331/333/354、既001のPT-MED-050～054及びMediaApplicationServiceTestの業務PTを参照する。起票時UI233表記は本資料のUI235等へ追記訂正する。元担当は現registryのMediaReplayFixture/MediaStageFixture=P009-01、MediaReplayServiceTest=P009-02を保持し、共通是正費を親子へ二重加算しない。

MediaStageFixture.goldenはTest WireMessage入力のheader.messageIdだけを期待電文へ渡す。MediaReplayFixture.wireの第二引数はUUID correlationとし、offset60へその文字列を入れる。Replay全10callerは元request九/current一の入力IDを渡す。Production MediaRequest.decodeを期待値生成へ呼ばず、Production decoderの呼出し・検証範囲を製品側又はSUT入力fixtureの責務に保つ。

## 独立source検証（製品PTではない）

|確認ID|入力/操作|期待と独立根拠|
|---|---|---|
|REV-MED-ORACLE-001|元source b120、対象三sourceと限定変換を照合|上記UUID引渡し以外の全文tokenが一致。GJFのcompile-time String結合だけ正規化し、元全assertion/byte配置/fixture操作を保持する。assert prefixを呼出し数としない。|
|REV-MED-ORACLE-002|相関をresponse/NEXTへ誤接続、Stage decoderへ戻すmetadata三変異|全てsource guardが拒否。元Test/DB/key/native/Rootを実行する変異試験ではない。|
|REV-MED-ORACLE-003|当固定sourceを正常Maven六module compile、旧qualified normalとのMain/Test class SHA比較|compile終了0/PT0、全Main1843同byte、変更classは対象三sourceに限る。旧実PT・coverage成功を新sourceへ転用しない。|
|REV-MED-ORACLE-004|当三sourceの所定PMD/Checkstyle|元raw指摘/終了値を保持し、適用性未完・未是正はF03未受入とする。抑制や除外で0にしない。|

対象正常/null/境界/異常/例外/競合/再送の業務期待値は元001のまま。DB/key/graph等に依存する動的PTはNOT_EXECUTED_HOLD、このsource確認をPASS件数/coverage/native/正式受入へ換算しない。新Test IDを製品PTへ追加していない。

## 再現

固定source 0867302e7c5eb95163213cb6340ac86f6898e137、正常tool pg10370_media_correlation_six_compile.py、静的pg10368_media_correlation_static.py、source post pg10372_media_correlation_post.py。PYTHONPATH/環境と真正終了・manifest/hashは006へ記録する。工具はnew-only出力のため、成功確認だけの再実行はしない。
