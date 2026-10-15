# 保持directory・非上書き公開の全scope個別受入

WBS-P003-04、2026-10-15、Production a9/PG2802、Test snapshot25e571bd1。専有七path＝DirectoryCalls、ExistingFileAccess、LinuxDirectoryCalls、LinuxHostDirectoryCalls、OwnedTransferDirectory、StorageIoException、package-info。六実行outer family（DirectoryCallsの拒否default含む）と全内部SAM/entry handle/NioIo/Reason、package注釈を対象とする。485/hashと同一、専有RD空、終了依存P002-02は同a9受入済み。FIL001～009の業務側結果全体をこの共通能力だけで認定しない。

正本origin/main756a891d9のSS333 §5/7.3～7.6、SS343 §6.10、SSC019/020/021/022/028/063/065/068/087/118/193を適用。SS333 localはorigin/mainと同byte。保持能力はcallerのroot/owner/ACL/同run/排他/真正停止の認証を代用しない。SS333の既存directory/通常fileを自動repairしない契約、公開/削除後sync失敗を巻き戻さず不確定な非成功として保全する契約を維持する。

## 全method群と独立期待値・Test ID

原Test IDはclass＋下表method群、全件の元ordinal/case名SHAと原XML/source hashは公開PG3316 manifestに固定。候補四Testに加え、private能力の追加三Testも同Storage23/163内から照合する。**対象七Test classの実62 methodは実3702の内数**。新62試験を実施・追加したとは算定しない。

| 全対象method/契約 | 実Testと独立oracle |
|---|---|
| LinuxDirectoryCalls factory/bind/openRoot/openDirectory/openEntry・segment | LinuxDirectoryCallsTest F01二method：Linux64bit/glibc必須、未知OS/ABI/欠落symbol/null/空/dot/dotdot/slash/NUL拒否。実temp rootを全segment NOFOLLOW、既存symlink/非directory不成功。errno17→COLLISION/2→MISSING/他→UNAVAILABLE、固定診断/causeなし。Linux/glibc実行済みで未知環境fallbackなし |
| 同createFile/createDirectory/publish/unlink/removeEmptyDirectory/sync/close | W01/F01/F03/TRANSFER003計五method：独立byte列1,2,3対7,8、0750/0640、100同時create/100publisher各winner一件と敗者原byte保持、既target/symlink保全。AT_REMOVEDIRはempty一childだけ、nonemptyの原file1,2とsymlinkを保持、再帰なし。無効FDは固定非成功 |
| LinuxHostDirectoryCalls全factory/openRoot/readonly delegation/拒否mutation | PT-OPS-HOST001～008：固定/proc/1/root・flags589824/mode0・euid0前置の独立call順、借用child openとowned closeだけ委譲。create/privatecreate/mkdir/private mkdir/publish/unlink/syncはdelegate呼出0で拒否。実ordinaryUIDも拒否、未知例外identity保持/一時Arena消滅、32並行pointer不混合。許可arch文字列の確認を実ARM機試験と誤認しない |
| OwnedTransferDirectory.open/openDate/openExistingDate/openExistingChild/atDirectory/close | OwnedTransferDirectoryTest F02/RD01/MED018019/BUG036：absolute非root正規化path・年1/9999受理と0/10000/null拒否、各segment symlink/失敗traversalで全FD close。existing readerはmkdir/sync/repair0、childはparent close後独立。root/dateをrename＋別symlinkへ置換しても保持側だけに書く。private stateLockを使いcaller monitorで停止せず、callback中closeは待機しFD再利用なし、close失敗時再closeなし |
| 同atPart/atReady/atPartHandle/atReadyHandle/atExistingEntryHandle/createPart/execute/withEntry/EntryHandle | 同W02/A04/MED018019/F02全16method：create時点0640inodeを所有、操作中nameを別byte/外側symlinkへ置換しても保持inodeの1,2,3だけ。属性確認前symlink/hardlink内容read0、null/欠落/closed/callback IO/algorithm/close/複合故障、全owned FD一回close・借用parent維持・部分fileを勝手に削除0。固定path-free理由、unknown Runtime/NPE/Errorを正常化0。共通例外順位は受入P003-08/ResourceScopeと接続 |
| 同publish/deletePart/sync | 同F02/BUG036とLinux F01/F03：UUID.part→ready RENAME_NOREPLACE→dirsync、collision双方byte保持、ready後sync失敗でも公開byte保持・失敗返却、通常cleanupは自分partのみ。公開済ready/rootを暗黙削除しない |
| 同createPrivatePart/publishAs/unlinkEntry・DirectoryCalls拒否default/Native private0600 | PrivateDirectoryEntryTest PT-OPS-PFILE001～008：手書きCONTENT65,61,49,10、0600/link1、CREATE_NEW、part/target/symlink原byte、scope内実FD一回close、借用root保持、rename/unlink後sync失敗の実前後file状態、32競合一winner/31part保持、無効/null/unsupportedはnative mutation0。保持root置換で外側byte9不変 |
| 同createPrivateEntry | 同PT-OPS-NFILE193001～004：単一固定名0600の生成時inode、callback途中の名前置換先9不変、null名/operationは明示IllegalArgumentException（他入口のNPE契約と区別）、unsafe/closedはmutation0。create/write/close複合時部分fileを保持し再利用拒否、16競合writer一件 |
| 同publishChild | ChildDirectoryPublicationTest PT-OPS-PDIR001～008：openDirectory→publish→parent sync→child closeの独立順、前後inode/devとCONTENT65,10一致、借用parent生存。targetがdirectory/file/symlink全衝突原byte9不変、source missing/file/symlink拒否、同名/null/closed拒否、各native点＋unknown/close複合、rename後故障を逆操作0、retained parent、8競合一winner |
| 同createPrivateChild・DirectoryCalls.createPrivateDirectory/Native0700 | PrivateChildDirectoryTest PT-OPS-CDIR001～008：new-only mkdir→child open→child sync→parent sync、0700/同dev・UID/空dir・独立child FD。既directory/file/symlink metadata/byte保全、unsupported mutation0、全四native点×IO/Runtime/NPE/Error・close複合の一close/partial保持、保持parent置換・8競合一winner |
| ExistingFileAccess constructor/read/walk/requireSize/NioIo | ExistingFileAccessTest PT-MED021～025：手書き1,2,3と48,000,004byte sparse file末尾11,12,13、256segment受理/257拒否、size0/負/null要素/unsafe拒否。root/nested/file mode・owner/group/size/link/型の独立変造で内容callback0、no repair。14個のopen/attribute/read/size/close/post faultとunknown compoundで全channel/child close・借用root維持、100並行/entry-root置換も保持inodeの原byte、外側9,9,9不変 |
| StorageIoException constructor/reason/Reason・package-info | F01/各failure helperで全三reasonと固定message/cause/suppressed、null reason拒否を確認。非実行package注釈はnull規約の範囲でscope照合、意味のないassertionやcoverage除外を追加しない |

Root admission・保持inode属性・ACL・filesystem適合性は別P003-05/06とcallerの前置gateであり、DirectoryCalls.openRootやO_PATHだけでこれらを認証済みにしない。`atPart/atReady`のpath callbackはfile-adapterの生成名/保持directory内だけで同期完結、callbackからpath/Channelをexportしない。保守publishChildも排他下namespace同一性がcaller前提であり敵対rename後の真正Backup認定には使わない。既public SPIのTest proxyは委譲/故障注入でありprivate FD反射取得ではない。

## 実結果・三criteria

PG3316 actual0は原PG3302全3702/542/1643を束縛してStorage全23/163と各実Test source/原XML SHAを検査した読取要約。静的六0/FES-flaky-notrun0/本六family LINE-METHOD-CLASS-BRANCH各miss0、PG3306 native28全1643Main/79resource/debug同byte・CRC0を001/112と公開whole manifestへ接続。OS/JDK/command/branch/snapshot・coverage・終了code/hashは同manifest参照。新Main/Test/実行/署名/VM操作0。期待値は上記literal byte/flags/mode/回数/順序/独立filesystem後条件で、Production encode/decodeをexpectedへ呼ばない。

contract＝全七path・含有型/全method群と正本/Test ID/独立後条件、scope＝485全ownedとshared所有不変更、quality＝上記同source実全体/全scope四miss0/正常/境界/異常/null/故障/並行/close。DB transaction/MQ再送は低位filesystem能力に非該当で各上位ownerへ残す。終了依存P002-02とstrict前/候補/後auditを確認して当leafだけ認定する。全PGPT/ITST・QA051final、正式1964/53、工数null、残603L115M0C470B、原/v3費用は未変更。
