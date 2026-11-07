# Logout MVC生成契約・共有fixture単体仕様

Program NK-WEB-002、主WBS-P015-04、AUT004/UI226/SS313314/PG-D363。対象はLogoutMvcConfigurationの全source/constructor/logoutControllerだけ。旧LogoutControllerTestのDB/HTTP/crypto業務処理はHOLDのまま、当Mainとは別。新whole LogoutMvcBeanPortTestを作り、元held Testのmethod抽出や隠れた代替実行は行わない。原matrixではNOT_IN_CURRENT_MEASUREMENT_REGISTRY、公開followup/保存proofの照合で当factoryの独立資格なし（間接旧成功は履歴）。既JMS envelope4/返信7等は既資格済みと確認し再演しない。

## 独立期待

|Test ID|入力/操作|期待値・根拠|
|---|---|---|
|PT-WEB-LOGOUT-MVC-BEAN001|public class/Bean annotation/宣言反射|@Configuration(proxyBeanMethods=false)、@Import WebMvcConfiguration一つ、public logoutController(LocalLogoutHandler)戻りLogoutController、Bean一つ。UI226/SS313の明示MVC登録、実ApplicationContext refreshなし|
|PT-WEB-LOGOUT-MVC-BEAN002|null handler、同じ借用handlerで二回factory|NPE message「Logout handler」、別々のLogoutController二object/実型一致、DB/wire/session/nonce/crypto/ログcallback一回も呼ばない。独立literal/型宣言、production expected生成なし|

既BusinessMvcBeanPortTest全6は共有owner fixtureの変更に必要な同source再資格であり新規件数へ加算しない。共有fixtureに元EncryptedWebSessionRepositoryのgetterを一つ追加し、同じlexical ownerを使う。既constructor/SessionPayloadCodec.close所有契約を保持、DBproxy/ID/random全callbackはassertで禁止。新Test内のRevocationPayloadCodecはpackage-private既constructorへpublic zero32byteと自前NeverRandomを渡すformat-only owner。暗号化/復号・nonce/key生成・API認証・session発行・秘密filereadはしない。closeはこの公開零copyのみ消去する。実credential/keyへの操作と同一視しない。wire facade/request registryは既resource-free constructorだけ、Thread/Connection/HTTP/brokerなし。

## 実行分類とscope

PT_DEFAULT：自己所有host有限JVM、対象whole class二つ、Mainはcurrent7aed/normal22084、Web/protocol/storageの既normal JARと明示pinned Spring/Session/JMS/JUnitだけ。API/bootstrap/batch runtime JAR、DBdriver、broker server、Spring context起動/実security chain、Cipher、held四型/Root/native等の初期化・呼出0。新Testの2件＋共有fixture消費者6件を同一一回のexec/sessionで8件実行し、classinitとnormal Main実行methodを受動照合する。callback未呼出をguard/assertで確認。未知依存・不確定ならUnit前にHOLD、拒否を探る試行はしない。

期待coverage対象は既Business三config＋新Logout一configの全4physical Code、LINE8/METHOD8/CLASS4未達0、BRANCHは命令分岐なしの自然0/N/A（100に補完しない）。新規sourceproofはLogout一つだけ、既三と全support型へcreditを付けない。no private reflection（public annotation/signatureだけ）、除外/exec union0。Test-only javac25 lint/Werror、PMD/CSとGJF、Main NullAway/SBは同byte22084/86を再利用し再buildしない。静的指摘は全件個別適用を判定し原exitを残す。独立postはGit/source/8XML/元終了/CRC/session/全normal physical/全実行Main method/classinit/四指標と支援scopeを別照合する。

null/欠落は001002、境界はBean一つ/二回のfresh生成、未知callbackはfailclosed、例外後borrowed ownerの解放はfixture外側。並行/再送/業務反映はこのstateless factoryの対象外、後続HTTP/実Logout/DB/CSRF/認証/Browser/native/CHR/451/親leaf未受入を保持。新Product2/既6再資格を分け、正式1964/53/工数null/QA051finalは更新しない。群開始1/3/6pp cap8、Main製造変更0、Test/fixtureの作成・静的・単体を並行的な一作業群で進める。
