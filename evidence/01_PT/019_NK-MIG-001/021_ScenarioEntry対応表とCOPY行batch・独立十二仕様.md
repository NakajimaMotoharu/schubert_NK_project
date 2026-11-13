# Scenario Entry対応表とCOPY行batch：独立12仕様

NK-MIG-001/WBS-P01903.02、MIG003005006/MIG-DAT004005/DAT004/FUN004、UI223/242/254・SS331/V002・SS34310.1.4 SSC348。ScenarioEntryCopyBatchは既PlacementMapと宣言済Rowを接続し、COPY前の件数・ID・game/file/order/index・共通created_atを検査する純metadata。実source抽出/Current全件数/本文正しさ/speaker-FK/実DB/COPY/transaction/権限は別未受入。

入力はnonnull placement とnonnull Row List、null要素拒否。件数はplacement.entriesと一致、target entry IDは一意。全rowの先頭五field id/game/file/display_order/entry_indexは対応表と文字列を含め完全一致、未知targetや欠落を補完しない。時刻は既Rowのcanonical UTCだけを使い、複数rowは同一created_at、空は空batch値として許容し移行成功を意味しない。List順やtarget ID大小でなく対応表のglobal Current表示順に保存/送信する。row文字列の再検証・再正規化/暗黙変換を追加しない。

保存Listはprivate immutable、入力を変更しても影響なし、返却rows変更不可。copyBytesは既encoderのencodeRowsへ同順fieldを渡し、header/SQL/terminatorなし・byte別所有。固定診断とnull契約、保存外部可変stateなし。

PT-MIG-BATCH001..012: 001 source2→target900/order1/game1/file500/index7、10→100/order2/game1/file500/index3、30→50/order3/game2/file600/index0の手書き三row全COPY bytes（入力逆順、target非昇順）。002 件数少/多、空map+空rowのzero bytes。003 同target重複拒否。004 同件数でも未知target/欠落拒否。005 game不一致。006 file不一致。007 display_order不一致。008 entry_index不一致。009 共通created_at違いと全row別時刻・同µs時刻許容。010 入力/返却List/返却byte所有と複数呼出。011 nullmap/list/row/encoderと固定redaction/安全例外・失敗後の独立正常値。012 8worker64task/Future各5秒/finallyshutdownNow-await10assert、全結果は固定独立GOLDENへ比較。期待値をProduction methodで作らない。

全6Main/14physical（新Batch1/Row1/Copy1/Placement4/Entry3/File4）を同source必要whole72（新Batch12＋既5suite60）単一execで検証、旧exec合算なし/newdefinitions12のみ。通常RootNullAway/lintWerror/PMD-CS-SB/GJF・個別適用性・CRC/init/XML/四counter/実JVMCodeを独立post、global451や実ETL受入を代用しない。元sourceの既成功は確認再演せず、新batch接続変更群のclosure品質だけを一度取る。

追加不足.9/2.7/5.4: 詳細.1/.3/.6＋製造whole12定義.5/1.5/3を一群.6/1.8/3.6cap4、必要normal72 .3/.9/1.8cap3。元費用/群開始見積り/SV上限保持、actual token/専有費null。haruka BUG2874/aru禁止・Root/native/DB等の個別HOLD維持、端末内のみ。
