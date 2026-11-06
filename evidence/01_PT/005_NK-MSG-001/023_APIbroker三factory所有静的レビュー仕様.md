# API broker三factory所有・静的レビュー仕様

NK-MSG-001、WBS-P005-03主担当、ProviderのP005-04は関連参照で追加費用0。開始4146、原.5/2/5pp cap6。ApiBrokerContexts全276行と必須callee ArtemisConnectionFactoryProvider、既関連5Testとその独立literal/ProbeFactoryを提供する既2Testを静的に読む。新しいfixture/実行操作を加えない。

正本UI231/SS312/321/343/354、SSC314/315/316/330/334。下表の期待は承認設計と既存Testのliteral順序・独立例外表から固定し、Productからexpectedを生成しない。API親部分構築とprovider設定失敗とlive closeは別契約である。

| Review ID | 対象と独立期待 | 原Test/資料 |
|---|---|---|
| ABRO001 | create/createRetainingUnknownはcredentials非null、MQ_API supplier・policy・lock・容量3のowners/phase/scratchを最初の取得前に準備 | SS321SSC315/316、Main ctor |
| ABRO002 | createOwnedはpasswords/provider/endpoint非nullを取得前に検証。password copyは取得/設定時には読まない | nullInternalPortsRejectBeforeAnyFactoryOrPasswordCopy |
| ABRO003 | SYNC→WEB_LOG→ASYNCの順で各一回取得、各正常nonnull返却だけを既容量へ格納、最後はfinal field格納 | fact315004NullAtEveryPositionAndCompleteOwnerHaveLiteralReverseCleanup |
| ABRO004 | 取得1/2/3位置のthrow/nullで未取得をcloseせず、既成功だけ逆順close。first SYNC失敗ならclose対象0 | everyPartialFactoryFaultClosesEarlierProfilesAndPreservesIdentity |
| ABRO005 | API親部分構築は元primary同一性と個別secondary逆順を維持し、providerのfatal優先表に一括置換しない | SS321SSC315、FACT334003 |
| ABRO006 | 部分構築では全必要close後にunretained secondaryのfatal graphを分類、same-object self-suppression回避、scratchはfinally clear | fact334003ApiPartialConstructionClassifiesOnlyUnretainedSecondaryAfterAllClose |
| ABRO007 | endpointはexact loopback、port1..65535、fallback/query/先頭0なし。HA=false、connector timeout3000、factoryにcredentialを保持しない | ArtemisConnectionFactoryProviderTestのliteral3件 |
| ABRO008 | SYNC1048576、WEB_LOG65536、ASYNC0の独立factory。共通12設定はSS321の値・順どおり | apiFact315004AllThreeIndependentWindowVectorsAndNullProfile、ProviderTest |
| ABRO009 | provider profile/acquire/policyを取得前に検証、windowを先に計算、取得一回、null/取得throwを推定cleanupしない | apiFact315001/004、hold316006 |
| ABRO010 | provider setter失敗12位置×4種は一度close、後続設定なし、設定primary保持 | apiFact315002 |
| ABRO011 | provider cleanup Error対非Error primaryだけfatal優先、その他はprimary保持＋別secondary、same-objectはself-suppression禁止 | apiFact315003 の独立4×4＋same-object表 |
| ABRO012 | suppression無効carrierの失われるfatal graphは一度close後に分類 | fact334004、TIE.attachSecondary静的読取のみ |
| ABRO013 | sync/webLog/asyncは別factoryのcaller-owned context。legacy注入のasync欠落をProduction complete profileと同一扱いしない | completeThirdProfileOwnsDistinctFactoryErasesCopyAndClosesAllOnFault |
| ABRO014 | openはstopping後にpassword/provider呼出しなし、fixed nk_api/SESSION_TRANSACTED0、copy長1..65536、返却前にcopy消去 | base8件/FACT334001 |
| ABRO015 | copy借用後の正常/null/Runtime/Errorすべてfinally消去、借用前supplier失敗の未返却copyは消去保証外。String/SDK内部copyも保証外 | invalidLengths.../fact334001、SS343 |
| ABRO016 | live closeはASYNC→WEB_LOG→SYNC、成功phaseだけ記録し失敗しても残り全対象へ試行。次closeは未確認子だけ、成功後全体closed=true | closePhaseRetriesOnlyUnknownFactoryAndNeverReadsSecretsAfterStop、FACT334002 |
| ABRO017 | live closeは全必要試行後に先行するdirect Errorを優先、その他では全個別failure graphも調べ、固定公開例外へ秘匿。scratch clearとunlockはfinally | closeTriesBothFactoriesAndPreservesFatalPriority、FACT334002 |
| ABRO018 | retained UNKNOWNはprovider/部分構築/live closeの失敗地点で外側を保持し、正常return/外側解放/同操作再発行へ変換しない | hold316007/Driver、SS321SSC316。子/保持は実行HOLD |
| ABRO019 | openとcloseの同じprivate final lock、stopping/closed/ownerClosedによる直列化。並行実測・provider時間上限/親budgetを読取だけで認定しない | Main読取。既関連Testに明示open-close競合の実測未確認 |
| ABRO020 | 原Testの26method（関連5source19＋必須helper/provider2source7）を設計参照として識別。credential/embedded broker/native保持/四held等は未実行のまま | 原全7Testのbody/helper読取、coverage null、新PT0 |

一次点検は取得した資源の集合と返却前/返却後の境界、反証点検は各位置失敗と確認済みphase集合から行う。通常compiler20990・静的20992への同一source hash結合だけを再利用し、成功確認目的のengine/Unit/実broker再演はしない。対象不明の拒否scopeを推定せず、レビューをPT実行免除/正式受入に変換しない。
