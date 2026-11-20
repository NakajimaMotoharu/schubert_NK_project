# Media配信開始後の書込みError

PT-MED-PORT010、WBS-P009-04/2、SS333 §11・UI237。最大1枠のmemory配信portで、固定Range 2–4の開始後にOutputStreamの最初のwriteで固定AssertionErrorを直接投げる。期待値は206・Content-Range固定値の開始1回、body取得1回、書込み1回、同じErrorを伝播、ソース取得とclose各1回。借りたOutputStreamは閉じない。次の同instanceで206と3 byteが成立し、取得・closeは各累計2回。独立根拠はSS333 §11と手書きRange・byte列。PORT009は応答開始前、PORT005はIOExceptionを対象とする。実HTTPやプレイヤーの挙動は本試験の範囲外。
