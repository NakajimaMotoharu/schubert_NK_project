# 2449 authority七箇所・独立oracle製造結果

2026-10-29、2448/PG-D791/既BUG1830-YKT1581、source b95a31982a8a6066a9608e56af5fd17d5665576e（dev-foundation、六既Testだけ/Main不変更/未配備）。先行savecb523fcc7/push10464真正0/origin一致。原群1.5/4/8pp・cap10/event2819を保持、元2391予実不変更。共有開始13/reset1793774153、最新fresh13/残87、終了値はAPI最小fieldを直接487へ保存し、専有費/N/Tnull・費用帰属不明を維持する。

## PG実装・独立根拠

SessionSecurityContextTest二（auth/assertIdentity）、SessionLoginHandlerTest#auth、ApiSessionInvalidTest#setActor、ErrorMvcTest#set、ScenarioControllerTest#setActor、SessionAccessFailureTest#setPrincipalの七callを、同Test-private exhaustive helper六へ変更。SS314§7.2.6のUSER→ROLE_USER/ADMIN→ROLE_ADMIN一個（ab7a1907d0861ca1b6d4181d674f98a73c13f8a4b897b86f655b5a30ce202a7b、origin/main byte一致）をTest固定String十二で選び、Production role.wireValue出力からfixture/expectedを生成しない。入力SessionPrincipal.role identityは入力選択だけに使用し、未知enumの暗黙defaultを設けない。

七callを元式へ戻し、追加helper六/定数十二だけを除去・逆展開すると元全source token一致。全assert/他fixture/認証構築順/null/例外経路は不変更。各role誤選択・固定値誤り、case欠落/重複、Production encoder再導入、別入力、assert/annotation/終端変異の66静的反例を全検出。SS固定二domain/六sourceの12結合は静的確認であり実PTではない。対象外SessionFormLoginTest/WebSecurityChainTestのactual encoder assertionはsource全byteを保護。

R09/BIZ007のcase責任・criteria/終了依存UNKNOWNは維持。source責任費P01502/P00706/P01506/P01624/P01607/P01502をG03.01変更担当へ再配賦しない。既Test IDの2065 R09～15へ結合し、helperを新Test IDへ加算しない。元G03/10426/job/実DB BeforeAll/新fixture-harness/実認証・権限・アクセス設定を実行・変更していない。

## 真正証跡

下表pathは本directory下`evidence/provisional/<folder>/manifest.json`。command・source/全input・branch/時刻/OS-JDK/runtime・report hashは各manifest/invocationとowned SLOT beginへ結合。既JDK25.0.4/Maven3.9.12/format-nullness-compiler/PMD7.28.0 record補正/CS14.3.0/SpotBugs4.10.4 Max-Low・除外なしを保持。

| folder | SHA-256 | 元session・終了 |
| --- | --- | --- |
| PG13343-authority-oracle-plan-v2 | 6c80c0be7cacc06a949e5fd6ddfe8e5afddd0c769f0bb61e5931d2f00059372d | manifest内部0、外側表示は出力切断で欠測・再演0 |
| PG13344-authority-oracle-preflight-v1 | 70b22623fd38efb3ed1185a3eb6e1bc3c30eb466e2dd476f7ed2465425929353 | 34098/0 |
| PG13346-authority-oracle-v1 | 310c52175ecb38fdab18ec14e791e0b240a38295e346322cfedad7b317d25de9 | 47806/0 |
| PG13348-authority-oracle-v1 | 1ef5997b694d1ed5f15ad2a673919aa0b9af8455facd8e8c14cb7e0c1944c8b1 | 41863/0 |
| PG13350-authority-oracle-source-post-v1 | 008b5e9fc37448d9f9a0d20cf585b372a99b7d9d6105cad3aac4d91ebcc6cbc5 | 86923/0 |
| PG13351-authority-oracle-v1 | a68b5fbaf9c55a936e19d5ae3ad85961dd71e985d3d31bfe4c0c12b83e1778ba | 67979/0 |
| PG13352-authority-oracle-v1 | 47f00d04795ae89630f764cb8b24d5501213ee55782d51bc87f34225a8cf7a0e | 27711/0 |
| PG13353-authority-oracle-v1 | 3ebfd70bbfc39fec5fa194685f0ea8cc4c631ae88a01a597a2ead373902a8050 | 26149/0 |

- 元13342/session29146/entry3d089c7cはimplicit unpackのValueErrorと反例handlerの型不一致により真正1/OUTなし/source変更0。開始SHAを保持しBUG2049/YKT1797先行起票後、別v2の明示一意guardで66反例・後続同66を確認。旧工具/失敗を変更・再実行しない。新plan外側表示の欠測を成功表示へ補完せず、後続独立source検証の真正0と区別する。
- 13344は元同SHAのglobal13253又は後続13304の診断multisetをpathごとに選び、PMD09136（ROLE_USER四回）一件だけ消滅/他43保持/CS0/processing0。PMD真正4/gate1を全品質PASSへ読み替えない。
- 13346当source六normal/package/format-nullness-compiler終了0/ProductPT0。13348 fresh同source六JAR・固定外部auxで全1843ClassStats完全一致、bug/missing/error各0。旧source/旧不完全auxの成功を転用しない。
- 13350は全1843Main同byte、Test1974→1978・旧削除0。対象六SourceFile closure59の旧55class差/他1919同byte、追加四はjavac synthetic UserRole switch class（field一/clinitのみ）と実metadataに束縛。既二synthetic switch field形は不変、rootにprivate helper六/固定field十二だけ追加。javap追加member除去後の旧全private/public宣言一致と全元token逆を確認し、compiler差を除外しない。
- 13351独立binary/六report/typed八反例。13352/53は995六SHAだけ・他989/全責任費/旧runtime/unknown二を保持、旧state oracle bindingは歴史欄へ保全。八metadata反例、wholeWBS audit真正1/HOLDを維持。485/486は既決定的bulk機械更新＋元byte/全field/独立post一致。

## 限定閉鎖・未受入

BUG1830/YKT1581はORACLE_SOURCE_SCOPE_CLOSED（七source依存除去と必要許可static）、BUG2049/YKT1797は工具一意guard範囲完了。元六classの動的DB/MVC/資源後条件/coverage、R09/BIZ007、全G03/F03/451は未受入HOLD。実PT免除やPT代替受入の新認定0。oracle依存除去七とPMD是正一は別計上、ProductPT/新TestID/正式受入増分0。

derived7746=Main1502/Test6244、累計原PMD是正1695、refs3349/pending1372/noRef4397。全体PMD実測source db33/8022と追加32（うち14未分類）を保持し、新source全体再解析と呼ばない。正式1964PT/53scope・個別17/190・工数null/QA051final保持。原本DBBackup鍵/native/stash7/Scenario3/Currentbaseline/保留二工具/私有raw非アクセス・保全。保存push後も独立必要PG/PTを継続し、小群/commit/PMO待ちで終了しない。
