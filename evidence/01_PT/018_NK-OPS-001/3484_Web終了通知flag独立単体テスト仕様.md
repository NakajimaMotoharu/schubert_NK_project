# Web終了通知flag 独立単体テスト仕様

PG-D1131/NK-WEB-002/NK-OPS-001・SYS002004/AUT002004/MON003、UI212226252253/SS313342352・361 WEB-REM002。Main WebRuntimeFailureSignal9a90ff25全28行、AtomicBoolean/Objects以外のcalleeなし・native/Graph/closeなし。元WebRuntimeRemainder wholeは同Test内のnative/fixture・WebNativeRuntime故障経路をHOLD、新fixtureはそのmethodの抽出・改作ではなく別programの捕捉flag責務だけ。元361の期待を当Sourceの個別契約へ対応付け、実プロセス終了/所有/UNKNOWN解放の代替にしない。

Production6b53efeec87f3ec36a840dd8e7759656cb4aee5c未配備、HEAD5a1ccdfac0b05c0bcea9448a5d772c697b169a82/dev-foundation。群18300事前0.5/2/4pp cap10、F03担当・元owner保持/追加費0。PG製造追加0。

|SIGNAL-VALUE ID|入力・独立期待/後条件|
|---|---|
|001|constructor flag nullはNPE拒否|
|002|同AtomicBoolean false→run true・繰返しtrue、callerがfalseへ戻した同objectにも次run true（別flagを作らない）|
|003|公開RuntimeException/ErrorのConsumer callbackで同flag true、元cause/message/suppressedを変更しない、値を保持/診断/graph探索しない。nonnull callback入力の契約、未指定null payloadの挙動は認定しない|
|004|自己fixed pool最大4worker・64独立taskでRunnable/Consumer半数ずつ→同flag true、future全完了・pool.close後isTerminated=true、worker識別は自己JVM countだけ1..4、ID実体を保存しない|

新WebTerminalFlagContractTest四method・一exec、expectedは手書きboolean/呼出前後同object/explicitThrowable identity/宣言64と有界pool後条件。worker数は実観測line SIGNAL_OWNED_WORKERSをpostへ回収して宣言4と分離、Test数を64へ水増し0。自己executor1/64task以外の新workerなし・任意外部process/threadへ作用0。normal14216/static14224/JDK25.0.4同byte再利用、元成功全回帰/署名を確認再演0。Compiler/NullAwayの現Main証拠維持。

18300 raw→18302全一Source/physical/CRC/session/XML/counter・自己worker count→18304独立四oracle/metadata否定/TestCRC→18308/10 registry→18312/14 WBS→18315 binder、3485結果。公開合成Throwableだけ・実認証/DB/MQ/HTTP/Root/native/credential/VM/Graph0。並行は自己所有pool、再送に相当する重複通知はidempotenttrueのみ、業務再送やscope停止を免除しない。branchが自然0ならN/A、line/method/class100との区別を維持し人工分岐/除外0。実時刻/環境/command/exit/input/Main/Test/hash/XML/exec/counter/BUGはmanifest、Failed/flaky/skipped/not-runは合格0。正式1964/53・歴史17/190/新受入0/工数null/全HOLD不変。
