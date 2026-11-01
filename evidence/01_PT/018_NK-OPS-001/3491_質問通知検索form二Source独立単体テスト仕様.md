# 質問・通知検索form 二Source独立単体テスト仕様

PG-D1134/QST/NTF/SCR020022/UI224236/SS313§5.1/5.2・SS314/323QSSREQ01/NTSREQ01。HEADda439852759cdd576fbee30acc24bb77ac796b6f/dev-foundation、Production6b53/normal14216/static14224同Mainbyte。群18360事前1.5/4/8pp cap10・主F03、元owner/costは485の対象Sourceのみ保持する。

全QuestionSearchForm/NotificationSearchFormとDTO二種、必要TypedFieldValues.requireUnsignedRange・AnswerState/NotificationType/UserRole enumを読了。314等の認証/DB/Graph/2065 view四種を呼ばない純粋なMap/List→NFC/trim/UTF8/date固定+09:00/enum/DTOの契約、PT_DEFAULT。既QuestionController/NotificationController/2065のmethod/fixture・元Test bodyを抽出又は改作0、1249旧別source成功の転用0。JDK初期化内部IO未知null、アプリ明示file/HTTP/DB/JMS/crypto/provider変更/実authority/Root/native/VM/worker0。Questionの供給role分岐はtrueだが実認証・認可grantではない。名前でHOLDを解除せずN/Q view四classはrecord/trueprobeなしを確認する。

新QuestionSearchInputContractTest QSFORM001..014: 空map USER/ADMIN既定/各getter/空Optional、USER username存在は空でもfield error・ADMINだけ許可、keyword256/username64byte・NFC後幅/超過、state空/ANSWERED/UNANSWERED/ERROR/未知、page空/0/負/min-int/999999/zero-prefixとplus/非数字/上限/overflow、Fromだけ/Toだけ/両側の明示UTC値、同日/閏年366日-1ms/翌日超過/逆順1ms、strict日付/年0000/不実在/format/多重/control、未知field・全field空list/多重、control/孤立surrogateと正常BMP/補助文字、null map/role/key/list/item、caller copy/immutable values/issues・異role入力独立、固定redaction/不正DTO変換。

新NotificationSearchInputContractTest NTFORM001..012: 空map/getter/空Optional/size50、type空/ACCEPTED/COMPLETED/ERROR/未知、同page正常/境界/不正、From/Toの片側と両側明示UTC、同日/閏年366日-1ms/次日超過/逆順1ms、strict不正年/月日/format、未知owner等/全field空list/多重、control/孤立surrogateとBMP/補助文字の検査経路、ASCII空白trim/空日付、null map/key/list/item、caller copy/immutable values/issues、固定redaction/不正DTO変換。

期待は手書きenum/Optional/page数表、固定JST入力2024-02-29→UTC2024-02-28T15:00:00Z・同日To2024-02-29T14:59:59.999Z、from2024-01-01/to2024-12-31は差366日-1ms許可・to2025-01-01は366日超過拒否。from2024-01-02/to2024-01-01は-1ms拒否。Production date/toRequest/codecでexpectedを生成0、独立Python標準datetime/codec/NFCを後続で確認する。正常/境界/異常/例外/nullを全二Sourceとして測定し、枝欠測は欠測のまま保持。immutable per-call/local構造に共有更新・再送がなく当scope非該当、並行を実測したとはしない。

command=checked entry18360→18362全二Source closure/単一exec/session/CRC/XML/四counter→18364独立26oracle/metadata否定/TestCRC二→registry/WBS/binder。3492結果に実時刻/環境/branch/source/input/Main/Test/command/exit/XML/exec/counter/BUG/hashを保存。公式filter/coverage分母/SS期待値変更0・旧execunion0・成功全回帰再演0、実Browser/全画面/DB/認証/正式/新WBS受入0。正式1964/53・歴史17/190・工数null/QA051final/全HOLD/451/G07G13F03全体を維持する。
