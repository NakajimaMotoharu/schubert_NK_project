# NK-OPS-001 Root入口 guard PT（Testのみ）

WBS-P018-03.02、SS343/354/SSC137143307・SYS002004/OPS009/UI212251。RootServiceExecutableAdmission.withSetpriv/admit、RootStartupPending.observe/native awaitLaunch。既存API/WEB限定・nonnullを検証しProductionの変更/QA/新SSCは不要。開始event1176低.1/標準.4/高1.2共有pp固定、実費/N/T/消化率null。

RootContextNoIoFixtureは**test配下のplatform同package**で既package-private RootStartupContext.Ioへbindし、全native I/O入口でcounter加算＋AssertionErrorを投げる。製造の公開API/反射/権限判定を変更しない。成功期待値はliteral StorageIoException.UNAVAILABLE/transfer storage operation failed、nullはNPE、I/O/callback0。mockがOS成功を返すことはない。

|Test ID / RootEntryRejectionTest|入力/操作|独立期待値|
|---|---|---|
|PT-ROOTGUARD-001 / guard001SetprivRejectsEveryNonServiceRoleBeforeAnyIo|MORNING/CLEANUP/EXPIRY snapshot・nonnullwork→withSetpriv|固定storage拒否、全Root Io0、work callback0。API/WEB以外の開始を認めない|
|002 / guard002ObserveRejectsEveryNonServiceRoleBeforeAnyIo|同三role・nonnullissued→observe|同拒否・全Root Io0。current/permit read前に判定する|
|003 / guard003AllNativeEntryNullContractsPrecedeIoAndCallbacks|withSetprivの3境界、observe3境界、nativeawait4境界、admit4境界を一つずつnull|各NPE、Root Io0/Capability/work0、admitはfileopen前に拒否。null以外のfixtureは既publicliteralのみ|

既Main558974ad9を変えずTest/sourceのみ固定し、六Production format先行→先行47と新3を含む実50PT/8suiteの新run→static三compile module/同757Main完全byte同一性（元a2eccから累積2outer+4追加）を確認する。未実施50を47+3の算術だけで認定せず、同source XMLの真正50を必須とする。Root context fixtureはnativeを代替成功しないため当negative PTだけの証拠であり、同source genuine Root/native資格は後続freshwhole/実経路で閉鎖する。

実行command/実日時/環境/source・branch/終了code/全case/TestID/coverage・static/hash/BUG等は新run manifestと1050結果へ保存。初回未実施、全品質/正式1964/53・工数nullは不変。Production変更群のRoot ELF+待機が一貫して揃い、本限定群後に必要fresh全回帰・独立資格・当source実経路へ進む。元3791の確認目的再演は禁止。
