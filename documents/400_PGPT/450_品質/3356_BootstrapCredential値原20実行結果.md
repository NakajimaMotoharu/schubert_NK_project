# BootstrapCredential値原whole20実行結果

2026-11-01 09:17 JST、3355/PG-D1077、Source6b53efeec87f3ec36a840dd8e7759656cb4aee5c、HEAD034827e5cedb1eac3df5dc34fbfa0c7bb681446b。開始2/4/7pp/cap10固定。元三Test/20methodと三Main全本文・独立fixture helperを確認し、変更/抽出/新fixtureなし。

証拠は `evidence/01_PT/018_NK-OPS-001/evidence/provisional/` 配下。SHA256は各manifest。

|工程|directory|SHA256|元真正終端|
|---|---|---|---|
|review/alias/source固定|PG17215-bootstrap-credential-values-review-v1|1927ca63534fcc82d78a3fe85f86f4e4ddea5e4f39f4ccfc49d377f052015f94|原実行に包含|
|原20/3suite|PG17216-bootstrap-credential-values-twenty-pt-v1|57c0aeeab750d8a6018dfea56c83cf2f82e4d620fbde731bdee1fef79674e8c3|44178/65662a|
|全三Source/CRC/session/counter|PG17218-bootstrap-credential-values-twenty-post-v1|558a9b4aceeae4b3541be0cadfe7586e71db7d08ff2fa55470094b4ef0872dbd|82445/48a6e2|
|独立67反例/20oracle|PG17220-bootstrap-credential-values-twenty-independent-v1|67425b36190ea32bc9ae6c588d8a0de10393eae56e45962adc0cde1a52b6208a|fcc2f4|
|credential固有設計trace補足|PG17221-credential-value-design-trace-v1|fdd3a1fc57baad6ba311bcae486dfb99a919c281de551292d5d1486ed19567e3|af1cb5|

全checked entry lint/body/終了0、F/E/S/aborted/not-run0。commandはchecked entry経由pg17216/17218/17220/17221（new-only、確認再演なし）。元JVM OS/JDK、入力Source/Test pins、元XML/exec、normal14216、静的六module14224限定既証拠はraw/postに記録。generic独立postのSS341/342/343 hashは保持し、credential固有のSS324/343/352とUI212/241/251、RD141/171を17221でorigin/main同bytesへ補足した。fetch3d1cec真正0・origin/main8b91944df5820535e23ba2469740f1c0aa94c447不変。DAT-009/OPS-009は既Mainの間接支援traceであり、この値PTだけで通知削除非連鎖や全startupを受入れたとはしない。形式/破棄/秘匿の直接観点は該当SS324/343/352である。

|Main（module bootstrap/package api.maintenance）|LINE covered/miss|METHOD|CLASS|BRANCH|判定|
|---|---|---|---|---|---|
|InspectorDbCredential|37/0|6/0|1/0|28/0|四counter100%|
|InspectorAesCredential|44/0|8/0|1/0|22/0|四counter100%|
|InspectorCredentialAccess|30/3|7/1|1/0|28/6|未達|

三Codephysical/NoCode0、計111covered/3miss行・21/1method・3/0class・78/6branch、strict全三gate1。Access.requireDatabaseFileは原20Testに呼出しがなく3行/1method/6branchのgap、到達不能/除外や別Source結果で埋めない。新二Source四100%と一partialを分離し、whole451へ昇格しない。

既存Test IDを次の明示pairで元XMLのclass/methodへ結ぶ（17221のID列とcaseMethods列の順番を暗黙zipしない）。

- InspectorDbCredentialTest：193=validUtf8AndNewlines、194=invalidEncodingAndBounds、195=ownedCopiesAndClose、196=concurrentOwnership。
- InspectorAesCredentialTest：105=validKeyAndVersionBounds、106=envelopeLengthAndMagic、107=versionAndLineBoundaries、108=base64AndKeySize、109=consumedInputAndCopiedKeysDoNotAlias、110=closeIsIdempotentAndRedacted、111=concurrentCopiesAndCloseStayConsistent、112=nullAndInvalidInputsNeverEscape。
- InspectorCredentialAccessTest：113=rootAclFileAndDirectory、114=ownedReadonlyFallback、115=inodeTypeAndMode、116=linkSizeAndUidBounds、117=everyAclBitAndShape、118=nullAndInputOwnership、119=concurrentPoliciesDoNotCross、120=errorsAreFixedAndNonMutating。

全IDはPT-DB-INBOX接頭辞。期待値はUTF8 codepoint/明示byte・境界65536、NKKEY1と独立Base64/padding算術、手書UAPI44byte LE golden・全bit反例で、同Production methodでexpected生成0。null拒否/NPE正常化なし、閉鎖後/コピー所有/入力wipe/redaction/private lockと競合を観測した。JVM内部copy完全消去や実inode ACLの真正性を主張しない。

Test専用SecureRandom byte列生成は使用true、実runtime key/credentialファイルはロード0・provider設定変更0。秘密原本/乱数key/encoded値をGitへ保存しない。三所有FixedThreadPool/各12・最大宣言36、task宣言502（201/201/100）、実生成thread数観測null。自己workerだけtry resource/Future5秒で回収、実Root/VM/DB/認証/権限変更/サービス/鍵ファイル/loader操作0。四held六native/RootFailed五/Cycle23/inactive十record/probe不在。新BUG/Source/Test/設計変更0。

fresh09:06used72/残28/reset1793774153・短期null、券/追加課金0。usage09:06:32 cursor3606a67831959d6553a09c7b67e2d5ca9fc1f5ba1b94b0f846db13179bcbdf13、N/T/配賦null、explicit新record0/coverage incomplete、次10:06:32。開始と同じ整数表示は費用0でない。原/v3/v4/v5/残予測・正式1964PT53scope/歴史17/190/工数null/QA051final/全actualHOLDを維持する。
