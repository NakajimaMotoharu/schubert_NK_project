# PG2572 reused Backup handle整合性

## v3実結果

actual0/testSource3ff47d1b43783511dff44209679c2d45491998c0/payload06b5e19c/server2dac6dd0、限定1PT/5case/FES-aborted-notrun0/javac warnings0/全Main CRC0/VM操作0。全4row/原本/Connection/client/advisory後条件成功、当2branch追加・残L799/M156/C9/B559。公開reused-pair-manifest-v3.json。旧v1/v2失敗は保持合格0、全体/正式/leafは未完。

v2/testSourcec251e8580 actual1/payload623876d0は異なる例外ClassのconditionalとJUnit generic assertThrows型推論がjavac拒否、PT未実行。v3はThrowable捕捉後にliteral例外型を必須assertInstanceOf、STALEの固定messageも検証し、型の範囲を緩めない。v1/v2失敗・logを保持、合格0。新試験構築だけの是正、Production/上位資料変更0。

## 初回新期待例外の構築失敗

v1/testSource626ab4ea3 actual1/payloadba6b8830。STALE_TIMEの型/範囲不正は既BackupStepRepository.validTime/既独立BackupStepRepositoryTestのIllegalArgumentException契約だが、新試験はIOExceptionを誤期待した。MANIFEST/非SKIP二はIOExceptionのまま、時刻範囲不正だけ固定IllegalArgumentException（message invalid backup observation time）と既契約へ合わせる。Production/上位仕様/業務期待値は変更0、旧FAILEDとlogを保持・合格0、v2 fresh namespace未実行。

NK-OPS-001/MorningDatabaseSession.Session.completeReusedBackup、SS341/343/353/354、WBS-P017-01.03/0670群subset・追加予算0。当a79/Main/Jarと全3650/current九native、資格済み2568/2570のselected execだけを全hash/Source/Jar同値で結合する。失敗v1や旧sourceを合算0。

PT-MDB2572-001：5独立業務日・literal reverse ID成功pairを隔離DBへseed、実beginResumeBackupで二SKIP作成。VALIDは正常complete＋当原本prior2観測、偽manifest digest・database非SKIP・config非SKIP・原本開始前の時刻はIOException。各caseのSQL全4row id/step/attempt/start/end/status/count/byte/errorをliteral独立oracleで前/後/close後に確認。正常化のためのDB変更0、原本保持、実Connection/client/advisory0。

command：固定PYTHONPATHで pg2572_reuse_pair_selected_test.py（二工具fixture PASS）→clean固定→pg2572_reuse_pair_selected.py。javac -Xlint:all -Werror・限定JUnit1PT/5case/FES-aborted-notrun0・全Main/fixture/native/依存hashとCRC0。actual未実行、実source/時刻/exit/XML/coverage/hashは取得後記録。元残L799/M156/C9/B561、全体試験へ追加件数合算0、正式1964/53/leafdelta0・global100/451/CHR/trace/終了依存未完。
