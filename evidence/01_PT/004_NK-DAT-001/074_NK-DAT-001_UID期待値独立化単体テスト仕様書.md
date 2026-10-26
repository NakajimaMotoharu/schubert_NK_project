# PT-DB-INBOX-125 UID期待値の独立化・限定単体仕様

2026-10-26、G03_UID_EXPECTED_ORACLE_FIX_V1、主G03.01/関連原P003-05追加費0、開始.5/1.5/4pp cap10、used28残72/reset1793513544。BUG1794/YKT1545、原033/007_inode・SS311/343§6.3/DAT009/OPS009/FIL006/QA046/SSC049/451。対象LinuxInodeSecurityTest.platformAndSymbolAdmissionの期待値だけ、Main変更なし。新Test IDは採番せず既PT-DB-INBOX-125を是正する。

## 独立oracleとPG変更

自己JVMのJUnit @TempDirをJDK Files.getAttribute(root,"unix:uid")で読み、Integer.toUnsignedLongでOS file ownerの独立expectedを得る。Production effectiveUidをexpectedに呼ばない。default create()と既amd64/x86_64/aarch64の三overloadを全てその値へ比較。各factoryがbindするsymbol/OS/arch/null/欠落symbolの既負例・固定例外/causeなしは保持する。これは同hostのadmissionであり実ARM検証ではない。

最終sourceの単一method/一suiteを閉じたcatalogで実行する。原Testの他八methodは起動せず、setfacl/process/ACL/getxattr/statvfs/file capability/foreign inode/保持原本/VM/Root/service/permit/DB/JMS/鍵/cohort観測や操作を一切行わない。class初期化のLinker capture-state metadata、factoryのsystem libc symbol bindと自己geteuid read-onlyが具体的なnative範囲。OS identity/permission/権限・アクセス経路は変更しない。既JDK FFM通常試験の--enable-native-access=ALL-UNNAMEDはこの自己JVMだけ、外部設定/hardening変更ではない。個別native/cohort受入をこれで解除しない。

JUnitTempDirをrun専用0700/umask077のtmp内に限定し、framework所有の空ディレクトリだけを生成/後始末。raw UID/TempDir名/実外部process情報はlogへ出さず、独立assertion一致とXML結果を保存。実行classpathは当normal storage jar/Test classと固定JUnit/外部依存だけ、API/Web/Batch/Bootstrap旧jar・既artifact操作を含めない。標準JUnitのTempDir注入以外のfixture lifecycle/extensionは使わず、method selectorを一件に固定、全class discoveryしない。

## Test ID・期待

PT-DB-INBOX-125: 自己TempDir owner数値→unsignedがdefault/三archの実UIDと一致。未知OS/arch・gnu_get_libc_version/getxattr/statvfs/geteuidの各欠落はIllegalStateException/固定message/causeなし。null三引数は明示NPE契約拒否。正常getter誤り/予期しない例外はFAILでNPEをcatch成功扱いしない。

Test-only static→source固定/正常六compile/PT0/NullAway-Werror→閉じた単一method/依存closure/自己tmp preflight→一JUnit/一exec/session→独立XML/CRC/全LinuxInodeSecurity source内四physical class counter/未呼出しnative method0・当static/Main非影響を照合。no-Code三interfaceはN/A、全unit四100は本限定一件に要求を満たしたと偽装せず未達を保持、全451は後続。同じ成功確認の再演でなくoracle是正後の必要再試験。新たなplatform拒否があれば再試行せず保全する。

実command/OS/JDK/tool/branch/commit/終了・input/expected/actual/coverage/hash/BUG/横展開は075とshared018 manifestへ記録。旧dd/52PTは旧sourceのまま保持し、新sourceへ転用しない。正式1964/53・17/190・工数null/QA051final/全安全HOLD不変。通常限定成功/commitで停止せず、残G03/PGPTへ続ける。
