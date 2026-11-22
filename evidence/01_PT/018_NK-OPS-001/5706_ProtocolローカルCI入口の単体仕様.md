# ProtocolローカルCI入口の単体仕様と結果

NK-OPS-001、WBS-P018-02/2、SCM-005（RD171）、UI201/243/261、SS352 §13・354。対象は `tools/quality/verify_protocol_ci.sh`。選定したワークツリー直下と既存のMavenローカルリポジトリを使い、Protocolの通常 `verify` を呼ぶ。リポジトリのCIサービス設定と六製品の承認、配布用SBOM・ライセンス・署名の判定は別の終了条件。

| Test ID | 入力・操作 | 独立期待値 |
|---|---|---|
| PT-OPS-CI-PRO001 | 一時Mavenルート、空白を含むローカルrepo、代替mvnw。別moduleのMAVEN_ARGSを指定 | Wrapperに固定offline/verifyとProtocolだけを渡す。試験skip無効、失敗黙殺なし、試験0件拒否。空白を一引数で保持し、引継ぎのMAVEN_ARGSは空 |
| PT-OPS-CI-PRO002 | Maven代替が終了23 | 入口も23で終了 |
| PT-OPS-CI-PRO003 | 引数欠落・存在しないrepo・追加引数 | 各2、Mavenの呼出0 |
| PT-OPS-CI-PRO004 | Protocolのpom.xml欠落 | 終了2、Mavenの呼出0 |

現入口は4件の局所契約、Bash構文・ShellCheckを通過。実Wrapperのversion probeでMaven 3.9.12／JDK 25.0.4を確認。既存PG42624のProtocol 171件と同単一exec、PG42664のPOM候補のProtocol依存・包装照合、PG42666の依存収束を参照する。今回、実Wrapperから入口の全 `verify` を再演していない。受入には現候補でCIサービスの有効化後に取得する個別の実行証跡が必要。
