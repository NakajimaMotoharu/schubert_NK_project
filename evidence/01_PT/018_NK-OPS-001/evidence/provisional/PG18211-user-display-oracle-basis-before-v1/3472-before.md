# User一覧・詳細二Source 独立単体テスト仕様

NK-WEB-002/FUN009/AUT002、SCR015017、UI225§3/5・236、SS313/332§User、PG-D1125。Production6b53efeec87f3ec36a840dd8e7759656cb4aee5c未配備・開始HEADa9df619924feded41687afed9110922830242939。群18210は事前1.5/4/8pp cap10固定、primaryF03/元owner参照費0。着手前判定は全本文/callee確認後PT_DEFAULT、3471の四Source HOLDを解除しない。

UserListViewModel204行（Row含む）＋UserDetailViewModel77行の全二Source/三physical、helper UserSearchForm/PageViewModel/TopBar/SessionPrincipal/AuthenticationContext/UserRecord/UserDetailResponseData/PagedResponseData/UserId/Role/State/IdValue/TypedFieldValuesの呼出境界をnormal14216へ固定。原Test/fixture/method抽出・改作0。新UserDisplayContractTestの全八methodを一exec実行し、N/Q一覧/明細・authority設定/ApiSessionInvalidHandlerを呼ばない。Source local表示role guardは実行true、実認証・system権限/DB/HTTP/CSRF/更新/token発行/暗号/鍵/Root/native/VM0。公開合成principal/DTO/time/Unicode/数値のみ。固定offsetJST表示/URI encode/NFCUTF8は実行true、named timezoneは本経路から呼ばず、一般JDK初期化IO未知null。

|USER-DISPLAY ID（method末尾）|入力/操作・独立期待の根拠|
|---|---|
|001|空Page(1,50,0,1,0,0)、rows/PrevNext空、filter同一・TopBar ADMIN/固定redaction・immutable|
|002|Page2/total101/3pages/51..100の50行、caller clear後も保持、URL A+space+plus+amp+あ→A%20%2B%26%E3%81%82を独立hexで固定。Row全getter/Lock・Login有/JST9h/millis/末尾、要求999の最終page補正・last Page2/51のPrevだけ、optional無し空文字|
|003|UTF8 C-byte EF（U+E000）<F0（U+10000）を独立byte順、同名ID昇順、重複ID/逆名/同名逆IDを固定IAE。public DTO境界の防御試験で実DB UK適合の認定ではない|
|004|invalid form、Page不一致、空/非空行数不一致、actor/form/data/collection/要素nullを拒否。responseのsilent修復0|
|005|invalid form表示はpage/rows/navなし、valid formの誤使用/null拒否、USER値はlocal ADMIN表示guardでIAE。認証/権限設定ではない|
|006|Data role二×state三×active数0/1/2×version0/MAX9、自己名の大小文字/他人、日時・creator/updaterの正確な15key/値・password非保持/immutable/redaction。上位User default/Version0/DIF016最大二を表示上だけ確認し実session発行の合格へ代用0|
|007|USER actor/別ID/count3と999を各単独不一致として固定IAE。DTOの負/1000は既unsigned型契約であり当factoryを迂回するreflection fixtureは使わない|
|008|null三とInstant.MAXの標準DateTimeException伝播（部分display未公開）、元caller list不変。secret/raw errorの保存なし|

期待値はUI/SS・手書きmap/ASCIIとUTF8 byte/固定Page数/時差+9hのliteral、Production formatter/wireValueからexpectedを生成0。36組の表示field整合を一method内で確認し36件へ水増しせず、JUnitは八件だけ。正常/境界/null/collection/順序/例外/可変caller copyを網羅、共有状態/送信がない純値の並行・再送は非該当で実業務PTを免除しない。

18210 raw→18212全Source counter→18214独立oracle/metadata否定→18218/18220 registry→18222/18224 WBS二面→18225 source/run結合・3473結果。normal14216/static14224/JDK25.0.4/全Main source hashを再利用、元成功全回帰/署名の確認再演0。各checked entryの真正exit/FESabort0・OS/JDK/branchHEAD/時刻/command/input/helper/Test/Main/class/XML/exec/session/CRC/hashをmanifestへ保存。未達を除外/旧exec合算しない。正式1964PT/53scope/歴史17-190/新WBS受入0/工数null・QA051final/G07G13F03/451/全HOLD維持。新quality八と普通5786参照を混同しない。
