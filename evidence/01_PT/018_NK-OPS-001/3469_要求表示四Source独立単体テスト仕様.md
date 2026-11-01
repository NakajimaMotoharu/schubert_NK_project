# 要求表示四Source 独立単体テスト仕様

NK-WEB-001/002・SCR016018019、UI224§2/3・225§4、SS313§4/QA048・314/331§9.4/323、QA048049/TST001..005、PG-D1124。Production6b53efeec87f3ec36a840dd8e7759656cb4aee5c未配備・開始HEAD4fb6484ae6366d4e714bd9295d60475de6d7bc26。群18190は事前1/3/6pp cap10固定、primaryF03・元owner P01618/P01104/P01616参照費0。PG責務を維持し既実装を点検、新Main製造予定0。

## Scope・独立性と操作境界

QuestionSubmitViewModel/QuestionAcceptedViewModel/UserCreateViewModel/ReceiptReferenceの全本文・四Source四physicalを対象にし、未実行部分を除外しない。新RequestDisplayContractTestの全十methodを一exec実行。純粋なform bind/immutable map・固定public principal/token/receipt/DTOだけで、元DB/MVC/受付登録 wholeのmethod/fixture抽出・改作0。Question/User form、SessionOperationToken/Principal/TopBar、QuestionDetailResponseData/typed semantic/field値/JstWireTimestampと必要id/enumの実calleeを確認しnormal14216 snapshotへ固定。JstWireTimestampのZoneId Asia/Tokyo初期化/UTC→JST変換/NFCUTF8/自己form buffer消去は実行true、JDK内部provider/resource IOは未知null。

実HTTP/session認証/CSRF処理/owner判定/API送信/DBlocator保存/業務質問受付/暗号/鍵/Root/native/VM/worker/現在時計操作0。PUBLIC_DISPLAY/非秘密の公開合成password text/UUID(0,77)/26zero receiptはfixtureの値のみ、実credential/session/token/受付済みの証明ではない。原本等への読取・変更0。QA048のfresh業務側DB照合/登録回復とQA049の発行・消費・再送・上限は別gateで未受入。形式値の保持を業務成功へ代用しない。

後続索引3430はReceipt例外graph・原JDBC三wholeの別scope、2087は静的値レビュー。今回四Mainの現registry資格を代替しない。元成功試験/全回帰/署名の確認再演0。期待値はcanonical UI/SSと手書きliteral/時差9h/UTF16 surrogate二個＝一code pointの独立計数、Production formatter/getterからexpected生成0。

## Test ID（REQUEST-DISPLAY001..010）

|ID|目的・入力/操作・独立期待|
|---|---|
|001|Receipt26字/QuestionID1と999999999999/固定millisを同一参照・値で保持、Crockford許可集合と固定redaction。真正受付の意味は持たない|
|002|null各/空/25・27字/I L O U/小文字/underscore/LF、不正id−1/0/上限+1/LongMAX、非millis nano1/999999/123456789をNPE/固定IAEで拒否。32bit等へ切捨て0|
|003|QSB purposeだけ新form、question空/同public UUID/空issuesnotice/表示username・immutable maps/redaction。別UCR目的/nullactor/tokenは拒否|
|004|正常PUBLIC本文とLF異常form再表示、同UUID/正常本文又は除去後空/既question issue/noticeをcopy、nullform/notice/actor拒否・immutable。実再送なし|
|005|正常/199/200/201文字と199emoji＋XTAIL、先頭最大200 code pointを独立repeatで期待、JST2026-11-01 09:00:00/receipt/TopBar/redaction/immutable map。実HTML escape/DOMは対象外|
|006|QuestionID/receipt/time+1ms/usernameを各単独変更して固定整合性例外。業務DB認可の実証ではない|
|007|null三/空body、ANSWEREDなのに回答日時欠落というSS323意味不整合、wireの非millisは拒否。DB追加microsecondの読取復旧は対象外であり、wire DTOのprecision契約と混同0|
|008|User追加default USER/enabled true/username空、public token、空issuesmessage、正確な五key/fieldsにpasswordなし・immutable/redaction|
|009|正常ADMIN/disabledのform再表示、conflict false/trueとusernameの固定issue、元role issueの保持/既定USER。公開fieldだけ、同token/notice/immutable|
|010|nullactor/token/form/messageの境界を各NPEで拒否、実認証/更新なし|

正常/境界/異常/例外/null/Map copy/Unicode/精度を上記で検証。並行・再送はこのrequest-only immutable値に共有state/送信がないため非該当、実API/業務再送試験を免除しない。Input body/passwordは公開合成fixtureのみ・通常エビデンスへrawを保存せず、値なしJUnit XML/公開hash/counterを保存する。

## 実行と証跡

normal14216/static14224/JDK25.0.4とsource全hashを結合、Main/普通Test不変更。18190 raw→18192 complete Source/counter→18194独立oracle/否定→18198/18200 registry→18202/18204 WBS二面→18205 source/run binding、3470結果へ。checked_python_entryでlint→真正body、FESabort0/終了codeとOS/JDK/branchHEAD/時刻/command/input/helper/Test/Main/class/XML/exec/session/CRC/hashを各manifestに保存。未達を人工呼出/除外/旧成功合算で隠さない。新quality十と普通5786参照を分離、正式1964PT/53scope・歴史17/190/新WBS受入0/工数null・QA051final/G07G13F03/451/全HOLD維持。
