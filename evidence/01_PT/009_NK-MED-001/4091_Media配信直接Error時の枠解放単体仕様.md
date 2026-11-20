# Media配信の直接Errorと枠解放

PT-MED-PORT009、WBS-P009-04/2、SS333 §11・UI237。最大1枠の配信portに、メモリ上のFileSourceとResponseを渡す。1回目はチャネル取得・response開始の前に、固定のAssertionErrorをFileSourceから直接投げる。同じErrorインスタンスが返り、response開始とソースの取得・closeは各0を期待する。2回目は同じserviceで合成Range 2–4を要求し、206・3 byte・1回closeを期待する。独立根拠はSS333の全異常終了での枠解放と固定手書き3 byte。元PORT005/006のIOExceptionとRuntimeExceptionの結果を保持。実HTTP・原本・セッション・配信ファイルを対象に含めない。
