# OperationFingerprintの公開値と検索の単体仕様

NK-MSG-002、MQ-006、UI241、SS324 §3／§6、451、WBS-P006-01/2、BUG-3796、YKT-2960。OperationFingerprintが公開する実装選択は宣言名INSTANCE一件である。

PT-IDEM-FPR-CATALOG001 は、valuesの件数1、名称INSTANCE、同名valueOfと同じenum、二回の配列が同一インスタンスでないことを固定期待で確認する。定義外・小文字はIllegalArgumentException、nullはNullPointerException。新規fixtureを既11と同じ製品class・単一execに選び、二つの公開methodを確認する。

実鍵、鍵輪、業務永続化、同候補の全六製品は別。既JDK失敗注入は隔離テストプロセス内に限る。生の追加命令不足は到達済み四指標と区別する。
