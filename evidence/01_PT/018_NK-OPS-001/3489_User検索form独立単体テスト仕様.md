# User検索form 独立単体テスト仕様

PG-D1133/FUN009/AUT002/UI222225236/SS313332・USRREQ01、対象UserSearchForm bind/invalidCharacter/getters/toRequest/toString全Source。Production6b53/normal14216・HEAD05a236befcd3fa58ec6b7502edc3f4745fd0f0fd/dev-foundation。群18340事前1/3/6pp cap10、主F03・元canonical ownerは485から読取し変更担当に付替え0。12新quality一suite、既UserAdminControllerTest/DB/認証/画面wholeからmethod/fixtureを抽出又は改作せず、以下SSの入力契約から新しい独立Testを作る。既Main/helperは不変更、新製造0。

PT_DEFAULT: 全Main132行とDTO UserSearchRequestData/必要TypedFieldValues.requireUnsignedRange（固定digit6/3）、Role/State enum初期化を読了。Map/List/String/NFC/UTF8/数値とpure DTO constructorだけ。jvm/javac/JaCoCo/owned slot/XML/exec以外の明示file/通信/DB/HTTP/Root/VM/authority/Graph/credential/crypto/native/provider変更0、一般JDK初期化IO未知null。新public literal PUBLIC/é/補助平面文字と64byteまでの境界のみ、秘密情報/実利用者入力なし。原controller wholeの旧証拠を新PASSへ転用0。

Test ID USRFORM001..012（新UserSearchInputContractTestの全12method）:

1. 空map→四値空/page1/DTO Optional.empty×3/pageSize50/固定redaction。
2. role空/USER/ADMIN×state空/ACTIVE/DISABLED/LOCKEDの12組→固定enum/Optional値。認可grantではない。
3. 外側ASCII空白trim/NFC e+combining acute→手書きé、NFC後32文字64byteを許可。expectedにProduction normalize/bindを使用0。
4. ASCII63/64許可65拒否、é32許可33拒否、U10000十六許可十七拒否の独立byte幅1/2/4。
5. page空/0/-0/-1/整数下限→1、1/2/999999/000002→明示正値、DTO page固定一致。
6. +1/小数/非数字/999999超過/整数上限/正負overflow→page issue・既定1、toRequest固定拒否。
7. 未知field/空list/複数list→form/各field issue、他値は保持・不正送信0。
8. C0/DEL/C1/孤立high/low surrogate→各field拒否、é/Ue000/正常surrogate pair許可。invalidCharacter各短絡条件の境界を独立literalで確認。
9. 未知/小文字role/stateは固定issue、既定文字列以外をenumへ送らない。
10. map/key/list/item nullはNPE拒否、catchして正常扱いする製品変更0。
11. 元map/list変更後もform/DTOは不変、issues map変更拒否。
12. 不正formのtoRequestは固定診断、redactionに入力を含めず、正常DTOのpageSize50/optional独立値を再確認。

全入力/操作/期待は新Test内の明示literal/数表、production methodでexpected生成0。locale/clock/worker/共有更新/再送は当pure scope非該当、複数bindの独立性はcopyと異入力で確認する（動的並行実行を実施済みとはしない）。invalid/nullをPASSへ数えるのは期待例外assertionが成立したTestのみ。

実command=checked entry18340→18342全closure/単一exec/session/CRC/XML/四counter→18344独立oracle/否定/TestCRC→registry/WBS/binder。3490へ日時・環境・対象commit/hash/exit/FES/全coverage/関連BUGを実測で記録。未達は未達のまま・手動除外/生成filter変更/旧execunion0。normal14216/static14224同Mainbyte再利用・確認だけの全回帰0。正式1964/53・歴史17/190・工数null/QA051final/G07G13F03全体/451/全HOLD不変更。UserSearchFormをauth/DB/HTTP/全画面受入へ拡大しない。
