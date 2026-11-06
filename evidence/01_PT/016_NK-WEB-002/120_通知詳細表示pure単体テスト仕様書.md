# SCR021 通知詳細pure表示 単体仕様

RD exact追跡: FUN-108, NTF-004, NTF-005, NTF-008, QST-004, QST-010。関連requirementの表示層の部分を検証し、要件全体の受入ではない。canonical行/hash・class/method/TestID/manifest対応は `evidence/PG20212-detail-projection-rd-trace-v1/manifest.json`。

NK-WEB-002/WBS-P016-21、UI224/236、SS313/314/323/332/351、PG-D349、NotificationDetailViewModel公開factory/getters/toString経由でprivate state/time表示へ到達。元未登録282の当sourceであり未試験との断定はしない。

|TestID|method|独立期待値|
|---|---|---|
|PT-WEB-NDETAIL001|completedHasExactFields|16key・完了ラベル・固定JST/本文/回答・questionHrefを独立Map値で比較|
|PT-WEB-NDETAIL002|allStatesHaveLiteralLabelsAndTimes|5状態の表示ラベル/指定日時、ERRORの固定code/利用者向け文言|
|PT-WEB-NDETAIL003|deletedQuestionsRetireAnswerAndLink|全state削除済みで本文/回答/リンク空・answerAvailable=false|
|PT-WEB-NDETAIL004|completedMayHaveEmptyAnswer|生存COMPLETEDでOptional空/空文字回答もanswerAvailable=true・固定リンク|
|PT-WEB-NDETAIL005|targetNullAndSemanticMismatchReject|対象id・actor/id/data null・type不一致/削除と本文の矛盾拒否|
|PT-WEB-NDETAIL006|immutableRedactedProjection|Map変更拒否・固定redacted/TopBar表示文字列のみ|
|PT-WEB-NDETAIL007|unicodeAndMarkupStayText|Unicode/markupを文字列として保持、HTML描画/エスケープ実証ではない|
|PT-WEB-NDETAIL008|parallelProjectionKeepsActorsSeparate|自己所有2worker/8taskのactor/状態表示分離・bounded10秒join|

Fixtureはfixed epoch/immutable DTOと合成display Principal（contextはTest内で反復文字から生成し記録しない）。期待JST/ラベル/URL/状態maskはUI236/SS323の独立literal、Production formatter/projectorをexpectedへ使わない。HTTP/DB/JMS/MVC/Root/VM/実session/key/held4なし。既NotificationController carrier Testを変更/再演/合算しない。

normalD8 PG20112/SB20114再利用、shared012/profile056の新8を単一sessionで実行、F/E/S/abort0・currentSource/CRC・四counter100・独立postを確認。compiler $1 switch classをreportへ保持しACC_SYNTHETIC/$SwitchMap/staticinit/空counterを独立検証、手動除外なし。command/環境/branch/commit/coverage/hashと障害は結果121/manifestへ記録。正式1964/53・新leaf0・工数nullを維持し、全SCR021/PGPTの受入とは分ける。
