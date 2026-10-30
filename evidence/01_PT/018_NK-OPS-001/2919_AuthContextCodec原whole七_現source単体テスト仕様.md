# 2919 AuthContextCodec原whole七・現source限定PT仕様

NK-AUT-001/AUT-001/DAT-009、UI226、SS314§6/352§11.2、PT-AUT-005-C01..04、BUG036/YKT032、WBS-P007-03。Production6b53/normal14216固定、原四Mainと原whole Test7/全helper/initializer読了、全四Source五physicalCode（例外Reason enum含む）を測定する。Main原baselineは全P00703、TestはUNKNOWNを保持する。current1803へ全四Source/whole suiteの重複無しを照合済み、旧sourceの成功やcoverageは転用しない。

群3310開始0.5/2/5pp固定。現source再資格と新機能・新TestID設計・正式受入は分ける。PG15434/専用launcherは元7Testだけを一fresh JUnit/JVM/session/180秒上限で実行し、F/E/S/失敗/timeoutをPASSへ数えない。事前lint0・専用15436postのdraftを準備し、元terminal true0の回収後に実RAWhashだけを固定して独立解析へ進む。

| 元Test method / 観点 | 事前条件・操作・独立期待値 |
|---|---|
| bug036CallerMonitorCannotBlockEncryptionDecryptionOrClose | 公開key32byte=0..31/nonce42×12/架空UUID・user7・ASCII a64、caller monitor下の別virtualThreadが5秒以内に暗復号/close；元JCE oracleと全byte一致 |
| independentEnvelopeAadAndDefensiveCopiesMatchExactly | DataOutputStreamの独立length-prefix六field/AES256GCM oracle、鍵/input/outputコピー/赤字化/owner保持 |
| currentPreviousAndEveryIdentityBindingFailClosedOnMismatch | current書込/previous読取、row user/UUID/鍵違いはINVALID、未知versionはKEY_UNAVAILABLE |
| envelopeMutationsAndAuthenticatedNonContextPlaintextAreRejected | NKENC1 magic/version/id長/nonce/tag/長さ/ASCII違い、固定typed例外のみ・平文を返さない |
| lengthVersionKeyAndNullInvariantsIncludeBothEndpointsAndClose | version1..16、cipher101..116、key32、N12両端/超過、null拒否、鍵世代pair、close後拒否/冪等 |
| jcaUnavailabilityIsTypedAndProvidersAreRestored | 当fresh子JVMだけprovider一時除去、CRYPTO_UNAVAILABLE、finally元provider全件同順復元assert |
| concurrentEncryptionHasDistinctNoncesAndCorrectRowBinding | 自JVM100virtualtask、nonce100個異なる・元rowで全復号一致 |

期待値はProduction methodを呼ばない元JCE/DataOutputStreamから算出。別Node24/OpenSSLの公開固定vectorでNKENC1/AAD構造とhashを相互検算する（製品byteの実測と混同せず独立oracle側の検算と記録）。keyはTest内の算術公開fixtureで機密ではない。nonce固定はgolden専用、通常constructorの乱数100並行とは分離。実credential/実session/秘密key/DB/JMS/network/VM/Root/Graph/権限設定/他JVMへ接続しない。JDK getCause/getSuppressedは固定一段assertだけでgraph探索なし。

専用postはcrypto=true、publicSyntheticTestKeysUsed=true、actualSecretKeysLoaded/actualCredentialValuesUsed/actualAuthenticationOrSessionIssued=false、ownFreshJvmProviderStateOnly=trueを明記する。sharedpurev2のcrypto=falseやContextHash専用NO_KEYSを流用しない。完全Jar closure/実Code/実XML/OS-JDKprefix/一sessionCRC/実execを解析し、line/method/class/branchの未達はそのまま保存、人工branchや手動除外なし。counter測定後の別独立postはSS正本origin/main・全TestID/source/実stage/hash/意味反例を確認する。

初回15434 draftは未使用hashlib importのpyflakes1・body/compile/JVM未開始で保存する。元draftを上書きせずnew15435v2はimportだけ除去、専用15436post draftとともに事前pyflakes0。開始予算は固定のまま、未完成工具lintをProduct失敗/PASSへ加算しない。

実行command：python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg15435_auth_context_codec_seven_pt_v2.py。source/Main/Test/launcher/Jar/hash・branch・command/実日時/exit/環境/coverageは元manifestへ、結果2920へ記録。正式1964/53・歴史17/190・工数null/QA051final/全HOLD不変。実行済みpost/原PTの確認再演なし。
