# SCR009 Animation件数の過大申告

PT-WEB-SCR009-COUNT-001、WBS-P016-09/2-照合、FUN-006、UI235 §5.2–5.3、SS313 §2。合成USERとMAIN、応答宣言1件、レコード0件を投影へ渡しIllegalArgumentExceptionを期待する。独立根拠はANLRSP01のTotal countがレコード件数であること、固定入力の宣言1と空Listの0が不一致であること。既WEB232は正常な0件・上限と超過、宣言不足側を確認済み。この試験は宣言過大側だけを追加する。純値投影。実HTTP、配信、認証、原本操作を対象範囲に含めない。
