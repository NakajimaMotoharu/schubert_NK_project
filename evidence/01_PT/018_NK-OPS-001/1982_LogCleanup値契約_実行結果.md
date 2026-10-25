# LogCleanup値契約・実行結果

2026-10-26、仕様1981/群2233、branch dev-foundation、固定source **8ba82083ec65abc6373b8454576dcbaee7d3e621**。Production Main最終e598a81から変更0、新Test一source四IDだけ追加。Main四unitはCleanupReason/CleanupChunk/LogCleanupProgress/LogCleanupSummary、外側の削除service/DB/commit/owned releaseの受入ではない。

## 実結果

新CLEANVALUE003～006、**4件/1suite成功**、failed/errors/skipped/aborted/container異常0。全4物理classの各counterがmissed0、合計line34/method7/class4/branch16、同exec・session PG9814-CLEANUP-VALUES/当class CRCを独立post9816で照合、class0/0を100へ変換せず除外/unionなし。手計算差分7/4/3、累積WARNING10、zero0、Long最大境界、各null・run/完了/三count不整合、拒否理由の変更0を確認。全1843Mainと六Jar展開全entry、旧1915Testclass byte不変・新Test一class追加を9822で確認した。元16/20等の旧source結果へ加算しない。

OS Linux/amd64/7.0.0-38-generic、実JDK25.0.4+7-1-26.04-Ubuntu、JUnit5.13.4/platform1.13.4、JaCoCo0.8.15、Maven3.9.12。normal9812の六module package/format/strict lint/NullAwayは0、PTは意図的未実行0。対象Main4 SpotBugs指摘/解析error0、新Test PMD/Checkstyle指摘/解析error0。Main全域PMD/Checkstyle/F03/451の合格へ外挿しない。

## Command・証跡

全commandはrepo rootで `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/<対応名>.py`。工具/固定helperも同commitへ保存する。各manifestは日時・元command/終了receipt・source/入力byte・依存toolhash/XML/coverage/reportと参照を保持、host原本はwork/pgpt-runs/PG379の同小文字run名。公開先は `evidence/01_PT/018_NK-OPS-001/evidence/provisional/`。

|run / tool|真正終了|manifest SHA-256|
|---|---:|---|
|PG9812-cleanup-values-six-compile-v1 / pg9812_cleanup_values_six_compile.py|0/PT0|e074d972cbaf56b94ba4d25a77e7368b4f53ccd91489be0fbc27f07ef3975c95|
|PG9813-cleanup-values-preflight-v1 / pg9813_cleanup_values_preflight.py|0/PT0|5f1a770473711ca42f1374d40e0456dd41580919d89d762e6520f161b9ca8344|
|PG9814-cleanup-values-host-v1 / pg9814_cleanup_values_host.py|1/PT0/保持|c47222d159197293adfbdebdf5a2ac50fea454ce5c0fb25fe63a17be32c2b2e5|
|PG9814-cleanup-values-host-v2 / pg9814_cleanup_values_host_v2.py|0/新4件|3aba49441d549d8bc492dc4b063b230ab464772bb8554eedc83ff0cafa6a1944|
|PG9816-cleanup-values-post-v1 / pg9816_cleanup_values_post.py|0/製品再演0|dcb4e2ecd05ff765c58269d572d016dee84a7516b8a8878a443f36a0b4f3ea94|
|PG9818-cleanup-new-test-static-v1 / pg9818_cleanup_new_test_static.py|0/PT0|adcb5717bbf2b560ef70ceb3a231198d6d36ca1e1fdd98831f2aec427a56da71|
|PG9820-cleanup-values-static-v1 / pg9820_cleanup_values_static.py|0/PT0|875fd84bb698c4f05eaeb46fe67628844723c17227aca1ca8b367d93e309f24e|
|PG9822-cleanup-quality-post-v1 / pg9822_cleanup_quality_post.py|0/製品再演0|c81ac2d6af515934be47f6e9fb12ea34fc7355c6beeeb17b6998cd387bb240c0|
|PG9824-cleanup-test-owner-v1 / pg9824_cleanup_test_owner.py|0/traceだけ|ac07bdb3152cb171996e913c48d01b63cf1ea75583a5a7584008b646756d456c|

9824は旧961rowを全field保持＋新Test一件をMain四件の原owner/costOwner P01707へ明示登録。現1795Java/Main965/Test830のうち1787（Main965/Test822）登録・未確定8は不変。原941・485/486の旧source58913の測定/予算/受入は書き換えず、当追加manifestを現在の補足として参照する。全WBS監査HOLDを解除せず、追加4IDはこの試験群だけで一回計上する。

## 失敗・手戻り・残件

最初のnormal呼出しは設定済pyflakes PYTHONPATHを省略してimport前にexit1。SLOT/child/製品試験の作成前、環境を正して新only normal9812が0で完了した。平台拒否ではない。原host-v1は工具BUG1764/YKT1515（4methodと4suiteの混同）、修正前起票後に元helper/run/失敗を保持し、別V2でEXPECTED_TESTS4/EXPECTED_SUITES1を意味別に定数化。V2実4/1と9822の旧20/4非該当・全XML/session/CRCで工具範囲を検証済み、fix保存commit待ち。製品障害/未実装TDD失敗と混同しない。

群開始0.5/2/6pp・上限10pp保持。共有利用枠の開始used14/残86/reset1793513544、16:14:40UTC時点14/86。共有丸め0は専有費0でなく、実token N/T・PGPT/PMO配賦・工数率null。終了観測とcursorはeventへ追記する。正式1964PT/53scope、個別17/190、QA051final、Graph9/9774-9776動的未実行、F03 Root11・実VM/Root/DB/鍵/native/permit/intent等HOLD、Protocol生成四helper厳密資格・G07未分類・全WBS監査未成立は維持する。次は既存全体の公開coverageから実際の未到達Mainと当byte/後続成果を照合し、既に全counter100の値型を確認だけで再演しないよう次群を選ぶ。通常の小群/commit/報告では停止しない。
