# 現Protocol全171件・単一exec実行結果

PG43646、WBS-F03/2-2-b。SS322・SS323・SS354、QA-054、BUG-3716／YKT-2916。Test IDの原一覧はProtocol全moduleの試験仕様書とPG42762の39元XMLに固定する。

- 独立期待値は元の固定golden、固定幅・field表、例外と境界用に定義した値。改訂は出典コメント二つ。製品Java、試験Java、期待値本体は同一。承認版からの独立再計算はPG43594。
- JDK25.0.4／Maven3.9.12、候補sourceは `2f2d7b7087347eb57c5602476f9031f065b634a5`。ローカルのオフラインMavenでProtocol一製品を包装し、全39 suite・171件実行／全成功、失敗・error・skip各0。元のTest ID集合と一致。今実行で固有Test IDは追加していない。
- 正規JARは再現した176物理のクラスhashが元JARと一致。JaCoCoの当単一原execを176物理と照合し、生の行3,639・メソッド1,432・クラス162・分岐1,080、各未到達0。コンパイラ生成分も読み込んだ。旧execの合算なし。
- Mavenの標準報告も対象内四指標100%。今回のMaven包装では書式検査を省き、SpotBugsのverifyを起動していない。Javaに差がないPG42762の元書式・静的解析結果を別参照する。現行CIコマンド全体と六製品451の認定は未実施。
- [PG43646コマンド・終了・個別JUnitとSHA](../018_NK-OPS-001/evidence/PG43646-current-protocol-package-v1/manifest.json)
