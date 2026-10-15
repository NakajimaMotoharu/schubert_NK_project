# DB fixture初期化失敗・所有cleanup横展開仕様（実行前）

2026-10-15、BUG1295/YKT1061、PG3368/3370、WBS-F03。915/916の先行968fe9c65、原PG3366失敗47 report case/一BeforeAll error（意図54の完走ではない）。初期52はprivate-static単純patternだけだった。全Testの三DBfixture/AfterAllへ拡張すると129entry＝単純未guard88/複雑6/既guard32/当該nullableDB stopなし3。対象は94file/104cleanup call、複雑六の中にはnullable crypto owner九callとpassword消去一callを含む。before.jsonに全一覧・元hash・位置・非該当根拠を保存、対象数増加を新追加scopeとしてevent0890へ事前固定した。

| Test ID | 操作・独立期待値 |
|---|---|
| PT-QUALITY-DBLIFE001 | 元ExpiryAuditRepositoryTestを実JUnitで起動、明示した存在しないPG rootで最初のinitdb execだけを失敗。元BeforeAll IOException/startedTest0/container failure1を保持、AfterAll二次NPEと未受領fixture.stopは0。これは診断expected failでありProduction PT成功へ加算0 |
| PT-QUALITY-DBLIFE002 | 全129entryのafter source/hash/guardをbeforeへ比較。94file104callは受領済nonnull時だけ元の順/同methodでclose/stop/消去、元nonnull正常動作を変えず、32既guardと3非DBscopeはbyte不変更。scannerは単純/brace guard・無関係if・literal/comment・未知複雑bodyをpure負例で検証 |
| PT-QUALITY-DBLIFE003 | 同sourceの必要一全3706/542/1643・全六静的0/FES-flaky-notrun0と同native28・全Main/resource/debug同byte。正常な全対象DB cleanupと業務PTを含め、counter100のみ/検索のみでYKT完了としない |

guardはNPEをcatchして成功へ変換するものではなく、所有未受領のTest lifecycle cleanupを行わない契約。Main/DB schema/外部仕様不変更、原本・配備・VM操作なし。constructorがDBを部分起動してから失敗する場合の全資源回収は本exec-前失敗の証拠で代替しない。関連fixture初期化例外/受領前のownerにも同じpostconditionを保持し、追加実証が必要なら未完として残す。

BUG1294の環境是正は別有限scope。関連runnerはserverの実PG root/18系version/実行binary hashを固定し、新-only PG3366-related-v2で元54/7を再試験。失敗v1のlog/XML/Maven1・二次NPE・47report caseを削除/改名しない。両scopeの真の終了後だけ台帳閉鎖、正式1964/53・個別15/190・工数null/QA051final保留・原/v3費は維持する。
