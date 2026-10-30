# 2731 Storage固定名称catalog 元whole5 単体テスト仕様

## 工具のidentifier誤判定是正（BUG2107/YKT1854）

元14646はraw Files. substringが既知nested enum型名へ一致して入口停止1、Product0/SLOT-OUT無し。旧entry凍結、新14647v2はidentifier境界付きFiles dotとConfig production/read呼出しを検出し、全既source/hash/body/外側init拒否を保持する。六scope入力（一正常・五負）を事前/独立postで検証、JDK IOやunknown fixtureへ広げない。元.5/2/4pp/whole5/期待値不変、Tool手戻りとして記録しプラットフォーム拒否の再試行ではない。14648は新一execの元5/全Source/自己initだけを独立検証する。

source6b53efeec87f3ec36a840dd8e7759656cb4aee5c/dev-foundation/Git6cdfed61397800c82f738dad43b43c5c43f7df0b。NK-OPS-001/SYS002/004/UI243/253/SS342/343、PG-D930。元ServiceCredentialIdTest79行4件/EnumValueCatalogCompatibilityTest85行1件、CredentialId全body/Kind・ServiceConfigFilesのnested Service定義と外側staticを読取済み。実行するのは固定identifier/owner/kind/順序/immutable/null/enum serialization metadataだけ。鍵/credential bytes/私有ファイル/環境/location/権限を取得しない。

ServiceConfigFiles外側はnative factoryをstatic生成するため当試験では初期化も許可しない。Testは別class ServiceConfigFiles$Service のenum定数だけを直接使い、外側production/read/constructorへ入らない。static nested型の直接初期化と外側class初期化を区別し、元wholeを改変せず自己JVMのclass-initログでId/Kind/nested Serviceの初期化有り・外側Config/Linux*の初期化無しを照合する。実VM/他process/native/keys/Rootの観測/操作ではない。ログは新SLOT/own-class-init.logへ自己JVMが書くクラス名/時刻metadataだけで値は記録しない。欠落・外側有り・Linux有りは合格にしない。

|Test ID|独立期待|
|---|---|
|OPS-CREDID001|API固定五名称/db-api,mq-api,api-context-aes-current,api-inbox-response-aes-current,operation-hmac-current、PASSWORD二/KEY三の固定順|
|OPS-CREDID002|WEB固定五名称/db-web,mq-web,web-session-aes-current,web-revoke-aes-current,web-log-aes-current、同二/三|
|OPS-CREDID003～004|合計10種/サービスdisjoint/immutable・owner、null service拒否|
|F03-ENUM-STO001|手書きenum名/filenames/owner-kind全10順、API/WEBの固定集合、enum ObjectStreamClass metadata fields0/UID0（serialization出力や実file0）|

expectedはSS固定名称を手書きliteral、Production getterからexpected生成0。Jar closureは一Source三physical、通常code Id/Kind二とcompiler synthetic $1一。$1はflag4128/SourceFile ServiceCredentialId.java/<clinit>()V codeLength40/hash ee7584ed10c19ff4b608b4343809a09137d06137957663a657e105f5134799d0、**codeあり**として保持し、標準JaCoCo enum-switch filterでcounter0であることを独立に測る。noCodeと呼ばず、manual除外/標準filter変更0、全Source closureから消さない。自然branch0や不足はそのまま記録する。

Main canonicalP00307、Test二UNKNOWN、primary同leaf/componentなし・event3122予定 .5/2/4pp cap10。開始actual0確認後14646 whole5/2を一回実行し14648で全input/六Jar/static14224・元XML/FES・真正終了/原ENV/一CRC/八metadata反例・自己init四反例・全三physical/ownerを独立確認。新Main/Test/fixture0、実DB/HTTP/JMS/VM/Root/graph/credential0。JDK25.0.4/Platform1.13.4/JaCoCo0.8.15・outer180秒。結果2732へcommand/環境/日時/hash/実際/coverageと残を保存。正式/工数null/全F03-451/QA051final/HOLD不変。
