# inode属性・六rootの個別照合仕様（全体統合待ち）

2026-10-15、WBS-P003-05、Production a9/PG2802。全専有六path＝InodeSecurityCalls（非実行interface）、LinuxInodeSecurity、StorageAttributeGuard、StorageIdentity、StorageRootInspection、StorageRootLayout。全内部FFM SAM/Inode/record accessor/constructorを含む五実行family、485所属/hashと同じ。専有RD空、FIL001～009/DAT009/OPS009は関連参照でありconsumerの業務全件をここだけで認定しない。終了依存P002-02は同a9受入済み。

正本SS333 §2/7・SS343 §2/6.2/6.3・SSC028/049/080/137を適用。metadata SPIはsecret内容を読まず修復・child process起動なし、accessAclの空返却は「ACL取得不能/なしの候補」であって権限や不在証明ではない。callerの厳密ACL policyが別必須。security.capabilityの不在証明はENODATA61だけで、ENOTSUP95を不在と見せない。WBS見出しのext4もStorageRootInspection単体の認証とはしない。適合filesystem/排他/全runtime readinessのcaller gateは別ownerに残す。

## 全method・独立oracleと実Test対応

既Storage全23/163のうち下記四class計21 methodに対応し、RootInspectionTestの既三methodは006の是正後after-v2で実成功。旧PG3316のTest ID/class名を識別参照とし、RootInspectionTestの**旧source hash/実行結果を新Test集合へ流用しない**。是正後のTest byteは2ad175fe、固定d2cf7759c、全163実XML/hash・coverage/static/Jar/UTCは公開PG3326 manifest、必要wholeはPG3330/3332/3334で別に資格確認する。

| Test / 全method群 | 独立期待値、boundary/negative/所有後条件 |
|---|---|
| LinuxInodeSecurityTest.actualAclAndUid | unix:uidの独立値をgeteuid unsigned結果へ照合。公開temp fileに独立Linux UAPI44byte ACL literal、UID12345をlittle-endianで埋込、actual setfacl→held inode→実getxattr全byte。返却copyの破壊後再読不変、limit43は実ERANGE拒否、truncateしない |
| filesystemFlagsAndFailures | statvfsの112byte・offset72のflagを0/1/2/3/上位bit/負値へ独立注入、ST_RDONLY bit1だけを判定。実filesystemのFileStore読み値とも照合、syscall非0は固定非成功 |
| heldElfCapabilityAbsenceRequiresExactEnodataAndNativeHeldFile | security.capability名・上限24、errno61のみ不在許可、95/1/5/34・戻値0/1/24/25/-2は非成功。実保持公開inodeで不在を確認、null/通常path拒否 |
| aclReturnAndErrnoBoundaries | maximum1/44/65536と独立0x5a byte列、zero/負/過長結果拒否、-1 errno61/95は空、その他errorは固定UNAVAILABLE。空ACLがpolicy承認とはならない |
| canonicalCapabilityAndBounds | /proc/self/fd/0・1・2147483647の正規形、別proc/PID/leadingzero/符号/child/traversal/非ASCIIdigit/2147483648以上を拒否、上限0/65537等/nullも拒否。正規文字列が実owner証明とはならない |
| platformAndSymbolAdmission / interfacesAndRedaction | Linux/glibc LP64・gnu_get_libc_version/getxattr/statvfs/geteuid全symbol必須、未知OS/arch/null/各欠落を固定拒否。UID全32bit符号境界は独立maskFFFFFFFFでunsigned期待。実不在FDは固定path-free/causeなし。許可arch文字列の同host検査を実ARM試験へ読み替えない |
| heldInodeSurvivesReplacement / concurrentReadsStayIndependent | inode名を別ACL UID12346のfileへ交換しても旧heldは12345、新openだけ12346。旧scope終端後の負例は非成功、100並行各ACL/UID/readonlyが不混合。全Arenaはlexical close、保持directory/entryはcaller所有scopeでclose |
| StorageAttributeGuardTest A01 | OS名owner/groupの小文字・underscore・hyphen・32文字受理、33文字/空/大文字/数値開始/日本語/slash/control/null拒否、固定REDACTED。immutable StorageIdentity全accessor |
| A02 directory / file | directory exact040750/link>=1、file exact0100640/link1、owner/group型と名の全欠落/null/未知型/不一致、通常fileとsymlink/dir/socket/device・special bits・余分grantを独立mode表で拒否。expectedSize1/48,000,000、0/負/上限+1、Long型の厳密一致 |
| A03実inode | 公開1,2,3byte、実mode/owner/group/hardlink2/symlinkで拒否、原byteと権限を自動修復しない |
| U01/U02 transferSize | part0/1/4799/4800/48,000,000を計上するだけ、readyは4800倍数の4800/9600/上限だけ。ready0/1/4799/4801/47,999,999、過長/負/未知型/欠落属性を拒否。計上は内容利用許可ではない |
| MED020 existingFile | transfer48MB上限は維持しmedia側1/48MB+1/999999999999/LongMAXの正サイズ属性を確認、各別size・mode/link/owner/group/欠落/型不正/null拒否。媒体N12上限や実hash/Rangeはconsumer別gate |
| StorageRootLayoutTest A05二method | 六getterとREDACTED、全15対の同一/両ancestor方向拒否、各slotのnull/相対/root/dot/dotdot拒否、同じ文字列prefixだが別segmentは正常。文字列前方一致ではなくPath関係を独立fixtureで確認 |
| StorageRootInspectionTest A07実root | 六実directoryをNOFOLLOW保持、asset/transfer0750・backup0700/各identity、他rootは通常directoryであること、SecureDirectoryStreamを必須化。変更mode/owner/group・symlink/missing/fileを非成功、null全入口拒否、現物repair0。BUG1289独立FD前後0→0、全held/resource閉鎖 |
| A07 metadata/provider | mode/nlink/owner/group各欠落/型違い/zero・backup不一致、非SecureDirectoryStream/null拒否。inspectOneの一般root確認は全六rootの完全OS account/ACL/filesystem readinessを代用しない |
| A08 inode/requireDistinct | 独立(dev8,ino200)/(9,200)/(8,201)は全別、同pair再登録だけ拒否。dev/ino各欠落/型違い/負device/inode0/null拒否、物理同一性はinode番号だけで判断しない |

## 実行・品質・残条件

既原Mainはすべてa9と同byte。関連after-v2実163/23、静的0、Storage LINE1172/METHOD257/CLASS37/BRANCH527全miss0。Main74は物理class、CLASS37はcoverage familyで単位を混ぜない。独立期待値はOS属性/UAPI固定byte/整数境界/公開file実後条件で作成し、Production methodでexpectedを生成しない。null契約・collection要素・typed metadata異常と並行・closeを含む。DB transaction/MQ再送/業務削除は本read-only guardに非該当。Main/JVM設定/coverage除外の変更0。

contract/scopeは上記全六path/全method/原文/独立Test IDで照合済み。qualityは新Test集合の必要全体3330→3332独立→3334同byte native28が**未完**。その真正終端・元hash・全scope整合後、strict auditの前/候補/後で当leafを個別適用する。それまではNOT_ACCEPTED、BUG1289/YKT1055も全体未完。正式1964/53・工数null・QA051final保留・原/v3費用・ITST未完は不変。
