# NK-ASY-001 空回答provider実行結果

PG190/STB001～005、選択試験成功・正式全回帰前。workerのDB/JMS/ACK/非同期フロー完成ではない。

2026-09-20 03:52:44 JST終了、38.323秒/exit0、新5PT＋既存Question16PT・依存FieldCodecTest/ResourceScopeTest成功、fail/error/skipped0。実行code2class/4method/10lineすべてmissed0、両classとも条件分岐なしのbranch0/0。抽象AnswerProviderには実行命令なし、coverage除外設定なし。NullAway/Enforcer/Spotless/SpotBugs成功。

command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,QuestionReceiptIdTest,QuestionSubmitRequestTest,StubAnswerProviderTest`。source d49cf119＋当変更/dev-foundation。Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12/JUnit5.13.4/JaCoCo0.8.15、tool追加なし。raw log `/tmp/pgpt-pg190-green.log` SHA256=`7b24db110764148a790d00e28d9cbf7c583ceecdd3392a88385edbf49270eac5`。

固定2時刻（nanosecond/1582年）・本文1/4096文字、null、未知clock runtime/error同一性、null clock結果拒否、値/固定redaction、64並行の独立時刻集合を確認。stub本体はclock読取のみでネットワーク/DB/logへの呼出なし。選択coverageの旧execを全体認定へ流用しない。

収集基盤の新012 scope追加中、初回019で新scopeのfullReactorManifest fixtureが未対応のため1errorを検出。これは未完成の新scopeを合格としていない段階の検証であり、新prefixをfixtureへ追加して40scope全source/run/hash異常・途中失敗停止を再検証する。Production障害は検出なし。正式source・実行時刻/環境/command・期待/実際・coverage/hashは正式成功後evidence/manifest.jsonへ収集する。
