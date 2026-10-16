# PG3952 重複literal隔離候補・静的試験（Main未反映）

BUG1330/YKT1096/PG-D420/WBS-F03、base7fff/PG3748を不変保持。候補は未commit全849byte-mapで識別し、base Git sourceを候補と同一視しない。Public/業務仕様の変更0、現VM/原本DB/Backup/key/native操作0。

| Test ID | 独立期待値・操作 | 結果 |
|---|---|---|
| PT-LITERAL-PLAN | 固定自作sourceの名前衝突/先行field/nested record/record/comment header/元input不変・重複request拒否/interface保持。4literalを一private定数へ集約、独立request/request/request/request出力 | pure3成功。初回helper依存IsolatedSourceOutput不足は新工具TDD compile失敗として保持、依存を明示し原本を書換えない |
| PT-LITERAL-PROOF | 全構文/member/type/capture/値/公開ABIを比較。許可したprivate/static/final/compile-time String fieldだけ正規化、使用回数固定、値/戻りtype改変を拒否 | pure3内で正負成功。hashはUnicode UTF-16 code unit直接処理、literal/source期待値をProduction methodから生成0 |
| PT-LITERAL-3952 | 原187findingの元sourceSHA/座標・型から実変換、全849copy/固定GJF、六moduleの同一性proof、生成70不変・原本不変 | actual0、187定数/71file、保留0、全六proof0。server SHA c9429fd3570e81bedab67eacb39cdd1ec997ad7fb67de545a077a197bbd371be |
| PT-LITERAL-3958 | 同固定PMD全rule/record overlay/typed aux・固定Checkstyleを全849candidateに実行、他rule件数不変 | actual0、PMD exit4/指摘1653（1840から-187）/processing error0、差分はAvoidDuplicateLiteralsのみ-187、Checkstyle exit0/指摘0。server SHA 9f9d8d9f33085d2c6472b3c930c24abedcb7ce327245d604f9e9c8c0a54ce194 |
| PT-LITERAL-STATIC-CLOSURE | 単一最終receipt/既固定rule/tool/zero Checkstyle/正確差分・未適用identityを確認 | pure2成功、途中PMDだけで成功manifestを作らない |
| PT-LITERAL-3960 | 全187/71/849・元/候補/静的hash一致、別source/別rule減少/生成物変更/既適用/部分scope/Checkstyle指摘を拒否 | pure2成功、実stage/applyは未実施 |

Linux/JDK25.0.4/GJF1.36.1(skip-reflowing-long-strings)/PMD7.28.0(record overlay既固定)/Checkstyle14.3.0。完全PYTHONPATHで対応script、実command/開始終了/全source/hash/候補/Module別proof/元findingと全使用位置/定数名/value hash/生成70をPG379/pg3952-literal-candidate-v1とserver同runに保全。独立fixtureは一時folderだけ、反射/coverage目的人工呼出し/到達不能扱い0。

**現Productionはまだ7fff/原1840/技術304/未分類1536**。候補1653を現成果へ混入せず、PMD exit4は全SAST合格ではない。F03/全counter100/正式1964PT53scope/受入17/190/工数null/QA051final保留を維持。次は元全849/生成70と71patchをstage/機械適用し、新Main固定→必要全回帰/native/CHR/451。旧native/旧caseを別sourceへ加算0、BUG/YKT全閉鎖は後続。
