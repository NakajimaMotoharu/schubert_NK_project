# NK-MSG-001 eventport 単体テスト仕様

対象Main: InternalEventProcessor.process(WireMessage<FixedPayload>,DeliveryMetadata) default。RD MQ-006/MQ-007、UI213/231、SS312/SSC153、649/650。Main canonical owner/cost WBS-P005-03。元Main Source6b53・対象SourceSHA b9d8a661…・normal14216 API artifact/class834643de…を固定。新Testは別source commit/hashへ結合する。既実装defaultはSSと一致しており、coverage目的でProductionを変更しない。

既InternalEventListenerTestの実broker redelivery後null二assertは独立期待値だけ参照、現在実行資格の参照が無いのでPASSを流用しない。新PTはSS312の純粋なdefault SAM引渡しだけを検証し、実broker/count/delay/queue/Root/旧readiness検証を実行するfixtureや代替ではない。2321の旧群externalprobe禁止は維持。DeliveryMetadataの既PG14244二試験は再実行しない。

|Test ID/method|入力/操作|独立期待値|
|---|---|---|
|PT-JMS-PORT001/defaultForwardsSameEventOnce|公開合成typed event、一回目/再送のmetadata count1/4、各fresh memory recorder|同じevent参照をSAMへ一回、順序変更/コピー/追加呼出なし。SS312互換default。broker再送回数を実測した意味ではない|
|PT-JMS-PORT002/nullEventNeverReachesBusiness|null event＋有効metadata|NPEで入口reject、delegate0。旧独立assert/nonnull契約、NPEを正常業務へcatchしない|
|PT-JMS-PORT003/nullDeliveryNeverReachesBusiness|有効event＋null metadata|NPEで入口reject、delegate0。同上|
|PT-JMS-PORT004/delegateFailuresKeepIdentityAndAreNotRetried|自己所有callbackが独立に作ったRuntime/NPE/Errorをthrow|元Throwable同一instanceを一回で伝播、callback1、正規化/再試行0。defaultはapplication TX/JMSのownerではない|

fixtureはCommonHeaderのEVENT/INTERNAL、認証context/result空、固定public UUID/Instant.EPOCH、data64/records0/total320、FixedPayloadを持つtyped model。wire encoding/実業務payloadの意味oracleではなく、opaque nonnull eventの引渡し参照である。入力modelのconstructor validationだけを呼ぶ。期待値はliteral回数/objectidentity/Throwableidentityから作り、Productionの判定methodから生成しない。transportMessageIdも公開合成値、実session/token/鍵/DBデータ0。

新TestにBeforeAll/外部fixture/グローバルextensionなし、標準JUnit Consoleの明示四methodのみ。API/protocolの固定normal jars＋新Test class/標準JUnitだけをruntimeへ置く。実行前にnewTest bytecode/SUT ABI/入力constructor閉包を確認、JVM class-init記録でAPIの許可二class（InternalEventProcessor/DeliveryMetadata）以外や他業務module/held Temp等の初期化0を検証する。pure moduleはPT_DEFAULT、実root/broker/DB/nativeは引き続きHOLD。

JaCoCo単一新sessionとnormal artifactから得た同一classCRCを照合し、一Source全physical class（interface一）を分析する。abstract SAMはCodeなし、defaultのみが実行可能で全適用line/method/class100を要求。Sourceにif/switch/loop/三項なし、branch0/0は自然N/A、枝hitを創作しない。java.util.Objects内部をSource branchへ捏造せず、null両境界は意味的negative testで検証する。手動除外0、private constructor反射/getter埋め0、別execや旧sourceの合算0。

並行処理/再送はdefaultがstateless・caller threadへ同期一回引渡し、共有mutable state/再送制御/owned resourceなし。delegateのTX/JMS/Question delivery-aware overrideや実並行再送は別終了依存で本sliceへ算入しない。四件のF/E/S/aborted0・真正OS/工具exit・Source/TestID/hash/OS/JDK/coverage/静的とtraceは004結果/manifestへ保存。元見積0.3/0.8/2pp cap10、初回Vへの差替え/新S-V枠なし。正式/wholeWBS/全451・CHR受入は独立に未完を維持する。
