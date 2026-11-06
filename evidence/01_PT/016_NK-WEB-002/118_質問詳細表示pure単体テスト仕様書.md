# SCR023 質問詳細pure表示 単体仕様

NK-WEB-002/WBS-P016-23、FUN質問参照/AUT owner・USER/ADMIN、UI224/236、SS313/314/323/332、PG-D350/368。対象QuestionDetailViewModelの公開factory/getters/toString、private label/projectionは公開factoryで到達。元未登録282の当class、既旧carrier Testが存在するため「未試験」とは断定しない。

|TestID|method|独立期待値|
|---|---|---|
|PT-WEB-QDETAIL001|answeredProjectionHasExactFields|answeredの固定id/owner/answer/JSTと12key、USER admin=false|
|PT-WEB-QDETAIL002|unansweredAndErrorHaveNoAnswer|UNANSWERED=未回答/ERROR=エラー、回答日時/本文空・answerAvailable=false|
|PT-WEB-QDETAIL003|adminMayViewAnotherOwner|ADMINは他owner表示、topbarはactor/row usernameはownerのまま|
|PT-WEB-QDETAIL004|summaryUsesOneHundredCodePoints|99/100/101個の補助文字・結合文字を独立固定literalへ比較、本文は全体保持|
|PT-WEB-QDETAIL005|targetOwnerAndBodyReject|id不一致/USER他owner/空質問/矛盾回答metadataを拒否、成功model返却なし|
|PT-WEB-QDETAIL006|nullBoundaryRejects|actor/target/dataのnullを入口で拒否|
|PT-WEB-QDETAIL007|immutableRedactedProjection|Map変更拒否/固定redacted文言、TopBarにdisplay stringsのみ|
|PT-WEB-QDETAIL008|parallelProjectionDoesNotLeakOwners|自己所有2worker/8task、各結果は個別actor/owner/summary・固定JST、bounded10秒join|

Fixtureは合成Principalとimmutable protocol record。synthetic contextはTest内で反復文字から生成し、値をlog/manifest/assertionmessageへ出さずreal sessionや秘密鍵は使わない。SQL/JMS/HTTP/OS/VM/Root/held4を呼ばない。Timezone期待値はUIのJST表示に基づく固定文字列でProduction formatterから生成しない。Unicode期待値も固定repeat/suffixから算出、Production substringを使わない。

normalD8 PG20112/SB20114を再実行せずsource/JAR/CRC再利用。新selected8は単一JaCoCo session、全実行成功・F/E/S/abort0と四counter100を実測して独立post。compiler $1 switch classはreportに保持し、生成code/no executable codeはjavap flagと$SwitchMapで独立分類。手動除外なし。環境/command/source/hash/coverage/障害は結果119とmanifestへ記録。旧Test/execの加算なし、正式1964/53・新leaf0・工数null維持。
