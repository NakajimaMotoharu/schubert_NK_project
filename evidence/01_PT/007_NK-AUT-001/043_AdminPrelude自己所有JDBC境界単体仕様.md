# AdminCommandAuthenticator 管理更新前置認証・自己所有JDBC単体仕様

NK-AUT-001/NK-ADM-001、WBS-P007-03、AUT002/003・FUN009・MQ004、UI225/226/236/241、SS312/314§9.2/332§12/SSC031。正本origin/main8deb209の「候補lookupは認可ではない→減員時のみ71419601→actor/target/必要active ADMIN昇順→session owner再照合→通常verify/ADMIN認可」を固定oracleとする。対象AdminCommandAuthenticator constructor/verify/verifyIdentity/owner/lockUsers/number/require・Mutation enum、全source/物理2class。元seed NOT_IN_REGISTRY、20458 strict pin無しを確認。元実DB試験を抽出/再演せず、新fixtureは手書きJDK Connection/Statement/ResultSet Proxyだけ。減員SQL文字列を観測するだけで、実advisory lock・ADMIN更新・session発行・driver・DB接続無し。

|Test ID|method|目的・独立入力/期待値|
|---|---|---|
|PT-AUT-PRE001|allMutationsUseIndependentOrderedPreludeAndUtcBindings|CREATE/ENABLE/DISABLE/PROMOTE/DEMOTE/RESET_PASSWORD/UNLOCK七種。DISABLE/DEMOTEだけadvisory、固定SQL順、actor7/target20・create候補7、HASH/UTC、target1/N12最大。既知64ASCIIaのSHA256固定vectorはPython独立hashで検証済み|
|PT-AUT-PRE002|targetPresenceN12AndNullContractsFailBeforeAnySql|constructor/API五境界nullは契約違反、CREATEにtarget・他操作target欠落・-1/0/最大+1はSQL前拒否。autoCommit/readOnly三不正組合せは固定Infrastructure、owner変更0。契約の明示requireNonNullを成功化せず、不意のNPEとは区別|
|PT-AUT-PRE003|candidateLookupIsBoundedSingleRowAndNeverAnAuthorityGrant|0rowはcontext拒否、null/0/-1/最大+1/複数rowは固定Infrastructure、User lock未到達、候補1/最大は後続認証が一致した時だけ返却|
|PT-AUT-PRE004|reducingAdvisoryAndSortedUserRowsRequireExactCardinality|advisory0/2rowを拒否、User0row/候補不在/重複/逆順/先頭0を拒否、候補のみ昇順は受理、増員/非減員でadvisory0|
|PT-AUT-PRE005|lockedOwnerAndFreshVerifiedActorMustMatchTheCandidate|owner変化/消失は認証拒否、最後のactor IDずれは固定Infrastructure、通常認証拒否を伝播。候補とWeb roleだけではgrantしない|
|PT-AUT-PRE006|verifyRequiresFreshAdminButIdentityAloneCannotGrantIt|DBの最新ADMINだけverify成功、USERはverifyIdentityのidentity返却だけ許可しverifyは固定FORBIDDEN。borrowed txn継続|
|PT-AUT-PRE007|ordinaryJdbcAndCloseFailuresPreserveBorrowedOwnershipAndRedaction|七statementのprepare/queryまたはupdate、全十三資源の各単独close SQLException、context primary+close SQLを固定redacted Infrastructure、未知Runtime同一object、既取得資源一回close/caller commit rollback close設定変更0|
|PT-AUT-PRE008|parallelFreshPreludeRowsDoNotShareActorsOrResourceOwnership|二worker32fresh row・個別Connection/actor ID、全Future/TWR終了、identity/資源混同0|

入力はsynthetic row・公開64a/hash・固定UUID/日時だけ、credential/実raw session/cookie/token/key/DB dump無し。SQL/並び/固定値/row数/closeの期待値はSSから独立に記述し、Production methodやprivate fieldから生成しない。AuthVerifier/AuthorizationServiceは純粋依存として通るが元6/2成功へ新規加算しない。生DBのlock直列化/競合/最後ADMIN保護/Inbox原子性や本番登録受入は別の未証明条件として保持。全四保留型・VM/Root/native/CHR/全451/QA055のHOLD不変。

normal20704/sourcefb189・全Java/POM同byteの静的20114を限定参照、Java25.0.4/JUnit1.13.4/JaCoCo0.8.15、profile091のprepare/static→source commit/push→一回8Unit→Git固定producer/config/SDK review/独立post。全2physical四countermiss0/CRC同normal/一session・FESaborted0を求め、旧exec合成/手動除外無し。SDK SQLExceptionのDriverManager getter初期化は既静的20846 JDK byte/新MainTest byte/実CP/init/XMLを別に結合し、syscall0や実接続の実測とはしない。元群見積1/3/5cap8/event4057固定。未実施/初回開発失敗をPASSにしない。結果044にcommand/実環境/source/run/coverage/BUG/hashを記録する。

初回20860 compile1（ContextHashのchecked例外宣言漏れ）/静的guard拒否は製品・Unit失敗でなく開発中の元結果として保存。20864 compile0/20866 PMD7のoperand内incrementをBUG2360/YKT2105修正前起票、cursor更新とyieldを分離。現20868 compile0/20870 PMDraw6/各用途非該当6/適用0/processing0/CS0。非適用は原行/所有根拠をpublic manifestへ記載し抑制0、元7を削除しない。PT-AUT-PRE007には普通provider IAE/DateTimeExceptionの固定分類も追加し、未知IllegalStateException同一性と区別する。予定8method/全2physical/原見積は不変更。
