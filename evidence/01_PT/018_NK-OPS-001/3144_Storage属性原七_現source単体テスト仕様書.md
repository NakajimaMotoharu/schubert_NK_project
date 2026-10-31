# Storage属性 原七 現source単体テスト仕様書

2026-10-31、PG-D1010、主/計測leaf WBS-P003-05（481 countsInTotal=true確認済み・旧accepted履歴の新受入0）。HEAD6393b593e3f3e28b4244b4c977b9a991cdd27809、Production6b53efeec87f3ec36a840dd8e7759656cb4aee5c/normal14216未配備。fresh18:58used57/rem43/reset1793774153/短期null/券0、専有N/Tnull。開始見積0.5/3/6共有pp cap10、原予測/leaf残予算を書き換えず、必要現source資格と工具・証跡費を分離する。

## 対象・独立性

NK-PRO-003/StorageAttributeGuard、StorageAttributeGuardTest全七。関連FIL001～009/UI237243/SS333§2・7/343§2/411/451、元2275/76/PT-SCN-008-A01～A03・U01/U02/PT-MED020の入力/期待/全methodを保持。先行index/旧11926/30と現全Test307行/Main103行/StorageIdentity/StorageIoException、旧launcher286行を全文確認。現2157registryに当Main/原Testの資格は無く、旧fd113e37の七成功を転用せず当normalで初めて測定する必要再認証。新Test ID/PG変更/元計画新受入0。

PT_DEFAULT。Map値/固定principal六methodと、自己所有の新0700親内の新子だけで合成3byte file・同子内symlink/hardlink・0750/0640/0644を操作するa03一method。既存file/原本/Backup/鍵/私有raw/実Root・VM・サービス・DB/JMS/ネットワーク・NK低level FFM/nativeは触らない。JDK Filesの自己新fileに対する実systemcallは有るため、実FS操作0と誤称しない。Test codeとJDK TempDir SPIのI/O、Production GuardのMap操作、工具/evidenceハッシュI/Oを別domainで開示する。

## Test IDと期待値

|原method|独立期待・観点|
|---|---|
|med020LargeAssetSizesKeepTransferLimitAndUnixGuards|1/48000000/48000001/long上限と0/負、owner/group/mode/nlink/sizeの欠落/null/型違い・実値違いを明示mapで検証。既存Asset正サイズとTransfer上限を区別。|
|u01SizeAccountingIncludesEmptyPartialPartsButReadyRequiresWholeRecords|未readyは0/1/4799/4800/48000000、readyは4800の正倍数だけという手書算術。|
|u02AccountingRejectsUnknownSizeBoundsAndInvalidOwnershipOrLinkAttributes|Linux sizeはLongだけ、欠落/Integer/文字/負/上限超過と各ownership field欠落を固定拒否。|
|a01NullInvalidAndBoundaryOsIdentityNamesAreExplicit|明示OS名32/33文字・大小/先頭/記号/Unicode/制御、constructor/API nullを既契約の拒否で確認。|
|a02DirectoryTypePermissionsOwnershipAndMissingAttributesFailClosed|型/特殊bit/0750・owner/group/整数nlink>=1を明示二進定数で検証。|
|a02FileRequiresOneLinkExactBytesAnd0640WithoutSpecialBits|regular0640/nlink1/Long正サイズ一致、特殊/type/許可bit/型/null/境界を独立定数とMapで検証。|
|a03ActualFileSymlinkHardLinkWrongPermissionAndOwnerRemainUntouched|新子の3byte regularを正値、誤owner/group・NOFOLLOW symlink/nlink2/0644を拒否。byte1,2,3とlink/permission不変更を明示比較、既fileに触れない。|

期待は元明示binary定数/数値/文字列と固定byteで作りProduction methodをexpectedへ呼ばない。原45＋27整数metadata検査は過去根拠として参照し再演0、元assertionを変更0。

## 実行・資源後条件・coverage

16274をchecked Python entryから実行、既未改変StorageAttributeFixtureJunitLauncher（SHA9ca2a53b0b475031b50b8872029a717a94249b4cfff166b1c5c0d004d66169b8）の閉七catalog/ja-JP/TempDirFactory/ALWAYS cleanupを再利用する。new-only自己slot/owned-tmpを0700/同uid/非symlink/空として作成し、各新子も0700・固定Test class/field rootだけ。七子がJUnit cleanupで消失し、親dev/inode/uid一致/mode0700/emptyが実前後同値であることを必須とする。元11926 slot/image/logを上書きしない。

原Test SHA1c0dd9629f7225661dd682f967ec0ae35fd1c93928144ed9349849d6ea1676c3、Guard d4752c82283b4ab0fc11b5ba738b32b5ce43045bab4576bc210fe4c4d50c635b、Identity e19734a40b13885ac0d62b3abb117a788d9a7e0839d002d5f655d162cce3cd74、Exception2a1233e46a8f05a0dbf7e42034ad3e34afecf14814ebf5111527db6b6e179284を現normalと全input/Jar前後で固定。JDK25.0.4/javac proc:none-Xlint-Werror、単一JVM180秒/単一exec、F/E/S/aborted/not-runをPASSへ加算しない。自己fixture以外のfs/権限変更0。

16276で一Source/一physical Codeの全四counter・CRC/単一session/四held六native無probe/実元環境/TempDir後条件を測定、16278で元七/XML・byte/数値/permission独立oracleと異常metadataを照合し、同source registry/WBS技術だけへ追加する。Guard物理method9のうち元から空のprivate no-arg constructor一はJaCoCo0.8.15既定PrivateEmptyNoArgConstructorFilterにより測定外（旧2276と同じ構造/既定filterを記録）。手動除外/人工reflection呼出しは追加せず、測定8method100%を物理9method全実行とは主張しない。正式451/全artifact品質は別未完。

実command/時刻/OS/JDK/branch/source/終了/hash/input・expected/actual/XML/coverage/BUG・self-temp後条件は3145/manifestへ保存する。原cost/正式1964PT・53scope/歴史17・190/工数null/QA051final/G07/G13/F03/全HOLD不変更、通常群/commit/報告停止0、残10以下/取得不能で保全する。
