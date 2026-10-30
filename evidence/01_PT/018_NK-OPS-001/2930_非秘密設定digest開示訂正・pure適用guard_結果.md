# 2930 非秘密設定digest開示訂正・pure適用guard結果

2929/PG-D942、BUG2129/2130・YKT1876/1877、source6b53/normal14216/current1831固定。旧15342/22f14eebはcrypto=falseと記載したが、原001成功のload→ApiConfigurationLoader.load→ApiNonSecretConfig.parseと原004直接parseは非秘密canonical UTF8へSHA256を行う。旧4Test/raw/XML/終了/exec/全二Code/未達2L1Mは保持、effect flagだけを旧post hashに束縛した追記で訂正。実key/credential/認証ではなく、元PTや既成功postの再実行0。対象の実fileはtools/quality/pg15342_api_startup_inputs_four_post.py（BUG2129初回subjectの末尾v2表記はrun-versionとの混同、旧エントリを保持しここで正記）である。

| artifact / evidence/provisional配下 | SHA256 | actual exit |
|---|---|---|
| PG15475-nonsecret-digest-disclosure-v2/manifest.json | f88a4e4ae812291db25fbb40084381bfd6dadc349c4bf2e3635597d03f137234 | 0 |
| PG15476-nonsecret-digest-disclosure-post-v1/manifest.json | 1c0d87141e7c9b3145aa2196db78347f43731f6306e4392dd6285ea3d90efa7b | 0 / 21反例 |

new sharedpurev3/f41c2d98は旧v2/4e23c3feを凍結し、新字句guard・全Main/Testへの事前呼出・version field/docだけを追加、全既解析AST不変を独立照合。guard31 metadata checkと別9checkで既知JDK crypto型/既知設定helper/単語境界/型拒否を確認、crypto処理には専用truthful profileを要求する。人相当の全helper/initializerレビューを置換せず、意味解析/全transitive call graph/新権限を保証しない。new libraryの既解析本体を再実行したとは称さず、旧資格とAST同一性を参照する。

現originalPostReferences内217登録Test＋tool source未登録1、残るresource系8登録Testを別に確認し、登録225/未登録tool1を区別。既知API/Web設定chain具体参照は15224/15302/15342の三postで、前二件はcrypto未指定（falseではない）、明示false訂正は15342一件。8resource系にはその具体参照なし。未指定をfalseへ補完せず、未登録tool/全過去/全間接helper/HOLDは未保証、検索だけで全効果分類完了やG13合格としない。

初回15474/036bc236はlint0/body1/OUT未作成、V2検証定数へv1/dedda4f1を転記したためpin guardが拒否。修正前BUG2130/YKT1877起票、旧工具保持、新15475/7997b6cdはV2定数と新OUTだけを変えて真正0。独立15476で三版本の別hash、v2のGit追跡byte・既15441の明示pin一致、旧失敗定数のv1一致と最小二差分を確認。原v1/v2/v3/既15441は非該当として元hashを保持し、Product/旧成功再演0。当工具限定修正で新機能/受入/工数を加点0。

effectiveCryptoOrKeyOperationsInvoked=true、effectiveOnlyReviewedPureValueSuites=false、SHA256_PUBLIC_NONSECRET_CANONICAL_CONFIG_NO_KEYS、actualSecretKeys/actualCredentialValues/actualAuthenticationOrSessionIssued=falseを訂正正本とする。domainは元Product/原Test bodyでありevidence hashやSDK内部bootstrapは別。旧ind15344は効果flag自体を検証していなかったため、その旧成功を新flagの検証へ読み替えない。元source/cases/全counter/gap/owner/XML/envはpreservedOriginalQualificationへhash付き保持。結果のWBS/current参照は2931/2932へ。

群3316元0.25/1/3pp固定、最初のevent書込は未登録workCategory TOOL_FIXにより書込前拒否、現487のCONTRACT_AUDITで正規開始し開始予算/元cursorを変更しない。これはplatform拒否ではない。実source/JDK/toolhash/日時/branch/command/終了/原証拠は各manifest/invocation、専有費/実tokennull・旧予算再配賦0。正式1964/53・歴史17/190・工数null/QA051final/全HOLD不変、PG/PT完了宣言なし。

旧15474失敗はchecked entryの返却観測（command: python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg15474_nonsecret_digest_disclosure.py、lint0/bodyStartedtrue/bodyExit1、entry036bc236）を本書へ保存している。OUT前停止のため元runtime manifestは無く、失敗実行の厳密開始時刻を後続時刻から推定しない。後続成功manifestを元失敗の実行記録へ転用しない。
