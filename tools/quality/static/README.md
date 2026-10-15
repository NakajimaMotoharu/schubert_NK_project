# PG3382 固定静的gate・初回診断

WBS-F03 / 411 §2,4～9,11,12 / SS354。Production scan前に規則を固定する。全`src/*/src/main/java`（package-info・生成recordを含む）を入力とし、除外・severity cutoff・抑制は追加しない。

- PMD 7.28.0: errorprone/security/multithreading三category全規則。規約のcorrectness/security/concurrencyを診断する。任意の複雑度閾値やPMDの独自format慣習を規約へ後付けしない。既NullAway/SpotBugs/Compiler/Spotlessは維持する。
- Checkstyle 14.3.0: 411命名・LF/tab・internal/wildcard import・空statement・equals/hash・fallthrough・file/type・宣言の構造。正確な整形は既固定Spotless/GJFが正本。規則一覧は隣接XMLを正本とする。
- 未分類違反、parse/型解決error、未処理suppression、入力欠落、canary failureは未受入。初回診断結果を見て規則を弱めたり例外を一括抑止しない。正当なSS/native ABI等の差異は個別に根拠を記録し、必要設計手順を守る。
- 外部tool binaryはGit外toolchainへ配置し、公式HTTPS入手URL・実hash・版・JDK・command・exit・全input hash・raw report hashを証跡へ残す。sourceは当a9の不変Main、compiled auxclasspathは終了PG3372の真正六Jarと同runの依存に限定する。成功済みMaven全回帰は再実行しない。

公式根拠（2026-10-15確認）: [PMD 7.28.0](https://github.com/pmd/pmd/releases/tag/pmd_releases%2F7.28.0)、[PMD ruleset/auxclasspath](https://pmd.github.io/pmd/pmd_userdocs_installation.html)、[Checkstyle 14.3.0](https://github.com/checkstyle/checkstyle/releases/tag/checkstyle-14.3.0)、[Java25対応](https://checkstyle.org/)。外部説明をcode/test期待値の代用にしない。

現在は初回診断の準備であり、F03受入・静的全gate PASSではない。導入時PMD scriptはJAVA_HOMEのみではJavaを発見しなかったため、固定JDK/binをPATH先頭へ明示する。最初のversion probe終了2と是正後version probe0を区別する。
