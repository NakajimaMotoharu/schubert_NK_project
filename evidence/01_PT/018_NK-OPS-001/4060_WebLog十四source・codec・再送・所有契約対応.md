# WebLog 14 source・codec・再送・所有契約対応

Program NK-MSG-002 / WBS-P006-04、RD MON003/MQ006008、UI213231235242、SS324§9/331/332/352・311/312/342、SSC007/321323/324/QA054。公開source全14と関連設計/候補TestのhashはPG26674 manifest。再送rowはAPI同1/5/30/60/300秒cap+±10%、worker polling1ms～1minを別に扱う。QA050失効15分をWebLogへ適用しない。

|対象|具体契約・独立期待値/Test ID|不足・現在の扱い|
|---|---|---|
|PayloadCodec/Identity/EncryptedPayload/PayloadException|PT-IDEM012015。NKENC1/AES256GCM/nonce12/tag16、AAD8LP field、2336 byte/全wire・Message/Correlation、current/previous/unknown、privateReentrantLock、clone/wipe/terminalcloseと原9の独立JCE・手組wire|元25758/25760原9は保存。pf173inputのうちProtocol3 source変更、現whole依存資格には未流用。同currentの必要通常再資格を次群で事前見積り後に実施|
|ClaimedWebLog/SendExceptionとReport|N12 ID・attempt0..100・workerASCII1..64・日時/identity/ciphertext/null・redaction、Report0..100とwidened合計|sourceと期待値対応、opaque ciphertextをauthenticity proofにしない|
|MessageSender/Dispatcher/ReplayWorker|PT-IDEM012/W01/GRAPH323/FAIL321。認証・全decode後にJMSopen、persistentTTL0/FQQN/dup、close/rollback/fatal優先、短DB TX分離、固定failurecode、worker interval/有限close0..30s/ownerjoin・callbacknull失敗|全sourceレビュー。direct actualWebStartup/実DB・JMSのwholefixtureはHOLD、pureなmethodだけ選ばない。元通常worker限定証跡は原scope保持、現全体へ転用しない|
|WebLogApplicationRuntime|PT-SCR127133/START324。reply→worker→HTTP起動、外側DB/factory/key借用、HTTP drain→workerjoin→reply停止、unknown時同startup frame/後続owner保持、再close/勝手回収しない|既helper1574のException/UNKNOWN範囲は履歴保持。startPathは取得済reply後のErrorをcatchしておらずhelper引数Exceptionである。不足経路を旧helper成功で合格にしない。普通Mainの直接callsite不在は到達不能除外ではない。Errorのstartup所有契約・許可された独立証明を確定してから是正/受入する。原/2内の残件として保持、現時点の不具合修正・PT PASS宣言なし|
|RequestLogMvcConfiguration/RouteInterceptor/SecurityAudit/package|Trace元10 input32、Audit元6 input9。登録route/安全actor/IP/閉じたevent/有限fixture/threadscope、metadataのみで認証許可しない|全該当input source同一を確認し元証跡限定再利用、成功再演0|

command `python3 -B evidence/01_PT/018_NK-OPS-001/input/1305_weblog_worker_public_contract_audit.py` は公開source/metadata照合だけ、PG26674真正終了0、新product実行/新定義0。actual四class binary/実鍵/DB/JMS/VM/Root/permission操作0。branch/core/source/日時/各原run・path/hashと未確認をmanifestへ保存。

原625 /1 .087/.227/.455ppの期待値対応準備だけ完了。/2、codec現依存通常資格、actual startup/DB/JMS/終了依存/451・元190は未受入。正式1964PT/53scope/工数nullを維持。起動・所有経路不足をmetadataだけで閉じない。計画説明・小群終了で停止せず、許可されたcodecの必要通常PTへ継続する。
