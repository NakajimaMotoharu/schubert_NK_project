# G13汎用oracle補助六件・担当候補結果

2026-10-26、仕様1985/PG-D673/群2238（.5/2/5pp cap10）、source8ba82083ec65abc6373b8454576dcbaee7d3e621、Main最終e598/Production-Test変更0。新しいfile担当候補6件を追加し、**1795Java中1793登録、未確定2**。Main965/965、Test828/830。99.89%はfile担当候補の登録率だけで、工数・全trace・PG/PT完成率ではない。

## 対応と境界

六汎用補助は@Test/Production型の直接参照を持たず、JDBC interfaceへのfault・件数観測又はcaller-lockの独立oracleを定義する。保守担当候補はWBS-G03、現在の登録作業担当はG13.07、consumerの業務担当は25参照全て保持した。参照数/多数決/moduleから業務主担当を選んだものではない。costOwner候補もG03だが、実費/旧eventの再配賦0・actualAllocatedPp=null/additionalSharedCostPp0。原941があれば原owner/cost優先、既962rowの全field/現変更Main bindingを保持して新6だけ追加（計968row）。

CallerMonitorProbe等は呼び出せばthread/JDBC delegateを操作する。今回の「補助定義の担当」は実行の安全性・実行許可・正常資源解放の認定ではない。sourceの読取と品質工具のmetadata unittestだけを行い、六probe・反射・JDBC/DB・Thread callback・対象Test・Graph9・native・外部環境の実行0。

残2はBorrowedJdbcFatal329Test/TargetBusinessControllerTest。既1936/1937の23method/26family/34関係は保存済みで、再parse/javap/再実行/再加点0。8source全てのbyteが旧64446と現8baで同一と確認し、混合業務Testを汎用補助規則へ混入させなかった。file primaryはUNKNOWNのまま、methodごとの既主/関連責任と実行未資格の境界を保持する。

## 再現command・主証跡

repo root、full PYTHONPATHで `python3 -B tools/quality/<tool>.py`。新工具は実行前pyflakes0。9834内の `python3 -B -m unittest trace_owner_probe_policy_test -v` は品質工具4method正常、六exact path/原logical優先/26近傍・横断Test不受理/作業担当と費用担当分離を確認。これは製品PT新4件ではない。

|公開run（018/evidence/provisional配下）/tool|実終了|manifest SHA-256|
|---|---:|---|
|PG9834-shared-probe-owner-v1 / pg9834_shared_probe_owner.py|0|0d361ca974427a14e3feab9ae8be3c55b704268da3576bd70cdfa52bd4bcf200|
|PG9836-shared-probe-owner-post-v1 / pg9836_shared_probe_owner_post.py|0|5fc8b6f8e3ce36b01c935ab557c70437674739c617d642d074393448c41f3011|
|PG9838-shared-probe-snapshot-post-v1 / pg9838_shared_probe_snapshot_post.py|0/元結果保持|edf63565cfb92793d61ecf7bae77717b4e0e4fbfdd0ab2a181e867caad3920d4|
|PG9837-snapshot-hash-guard-witness-v1 / pg9837_snapshot_hash_guard_witness.py|1/工具反例再現・製品PT0|6597b953453980a07e589b1bca22592a00c75e1fc7bc0edfa2b7e97b8dfb6888|
|PG9838-shared-probe-snapshot-post-v2 / pg9838_shared_probe_snapshot_post_v2.py|0/最終metadata資格|07273b18c8f3923fe3efed5a7ea2e163e9053ef8de1a4e1c24eed4ca41491600|

全source/hash/consumer line/owner一覧は9834のconsumers.jsonとmanifest、独立9836は原owner/全8byte/原962field/consumer25/source1795集合を再照合した。485は先頭のcurrent二sectionだけ更新、486はinventorySha256だけを現raw e75b5cf6へ束縛。原941/歴史943 dataset、予算、snapshot source/受入意味を9838で独立検査した。全WBS監査は前後とも**真正exit1/current physical candidate exact Git/worktree scopeでHOLD**、sourceの違う旧成功からPASSを作らない。

## 工具是正と編集手戻り

BUG1766/YKT1517は9838 v1の内部検査関数だけにraw hashとJSON再直列化hashのORが残った潜在弱点。外側mainの実raw assertは厳密で、v1の現metadata束縛/監査1は元から正しかった。修正前起票→9837の自己所有metadata反例で非原byte hashの内部受理をexit1として再現→別V2でexpected raw hashを明示引数化しfallbackを廃止、同反例/不正hash/未確定消去/owner・費用・実行権限・受入捏造/旧履歴消去・変更/未知field等11反例を拒否した。元工具/manifest/実1反例は保持、製品失敗/実行PASSに混入しない。

V2は原v1のinventory/snapshot byteとsourceが今も一致することを先に確認し、元before/after監査1を回収した。確認目的の全WBS監査反復・製品PT再演0。9834/9836/旧9808は元からraw SHAのみで非該当、既writer/consumerの業務担当を変更していない。限定工具scope検証済み・fix保存commit待ち。

metadata編集の初回apply_patchは二hunkの順序が実ファイルと逆で、変更前に拒否された。原hash60b210e1の不変を確認して実offset順のcompact二行patchを適用、486も一行だけ更新した。編集手戻り一回であり、セキュリティ拒否/製品障害/業務再試行ではない。

## 予実と継続

開始used15/残85→17:16:27UTC観測used16/残84/reset1793513544。共有差+1ppはPGPT専有費ではなく、token N/T・PMO配賦・実費・工数率null。原/v3/v4/v5予算、原見積り、開始.5/2/5を不変更。新規計画受入0、担当候補6、工具是正1、source再認証/既成果参照を分離する。終了quota/cursorはeventに追記。

正式1964PT/53scope、既17/190、工数null、QA051final、全WBS/G03/G13未受入とGraph9/全actual各HOLDは維持する。次はG01のcompiler生成switch-map四class/未到達16probeの**未完適用性レビュー**について9726等の既証跡と後続資料を照合する。生成helperを恣意的に除外したり、故意に不整合classpathを作ってcoverageだけを満たす試験を追加しない。通常commit/登録/報告では停止しない。
