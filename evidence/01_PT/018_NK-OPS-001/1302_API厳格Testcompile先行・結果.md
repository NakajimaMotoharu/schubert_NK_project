# 1302 API厳格Test compile先行：実行0、PTではない

元exec38858/pg6153-api-test-compile-preflight-v1、source **67bd94fe1320b4eed1aaf834e30605dd1359df45**。2026-10-20T18:42:22.007041Z→18:42:56.735850Z、真正0/Maven0、source固定、全851Mainは元c51と同byte。固定JDK25.0.4/Maven3.9.12、通常自己所有host、新onlysource.tar SHA **df950e09dafa473e18fd00ba499a36695d6e710d64ea54e0526cd8c81f17efd9**。

commandはpg6153工具の `mvn -B -o -ntp -Dmaven.repo.local=<固定toolchain repository> -pl src/schubert-nk-api -am test-compile`。既POMは不変更、format/enforcer、protocol/storage/bootstrap/apiの既Main型null・全Test-Xlint:all/-Werrorまで成功。**JUnit実行0/TEST XML0/JaCoCo exec0**、coverage未測定、SpotBugs六module成功や実行PT/正式/代替PTへ加算0。完全旧Test javac argvは未保存のまま、再現済みとしない。

公開 `evidence/provisional/PG6153-api-test-compile-preflight-v1/manifest.json` と私有PG379同run/manifest.jsonは同artifact。原compile log/入力/command/終了時刻を私有保存。BUG1555/YKT1313のcompile欠陥は是正確認済み、close機能は次1955件の実PTを要するため未完。次は管理証跡だけの保存commit（src/build/rule tree同一）後、新only6154-v2へ一回。source/runの違いは維持し、compile先行0を当PTの合格へ輸入しない。
