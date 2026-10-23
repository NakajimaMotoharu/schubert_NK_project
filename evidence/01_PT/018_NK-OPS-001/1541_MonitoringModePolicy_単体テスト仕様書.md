# 1541 MonitoringModePolicy 単体テスト仕様書

実行経路是正（期待値不変更）：PG7000は六format1/PT0、PG7004は六format0→依存Storage no-testsで1/PT0。BUG1645/1646へ修正前起票し旧証拠を保持。新PG7006は親POMのEnforcer/Java25/lint/Werror/NullAwayを継承する限定harnessを新only snapshot内で通常verifyする。原batch三Main source/一Testだけをcompiler includesで選び、failIfNoTests=true・四JaCoCo check100・SpotBugs Max/Lowを維持する。六formatは先行。依存業務moduleのPTをskipした成功とは主張しない。harnessはProduction module追加やPOM品質変更でなく、限定部品PTの工具（全体451は別に必要）。冒頭のPG7000予定manifestより、実原job別manifestと後続1542を優先する。

2026-10-23、group1797、Program NK-OPS-001/P018-09。SS351§8～10/UI252§5/RD171 MON010～013を正とし、PG-D517。C07監査で判明した元計画内の製造不足であり、C07の既監査見積には追加しない。着手見積0.5/1.5/3pp、上限10pp、共有表示6/残94/reset1793306748。工程成果とP018-09/C07全受入は別。

対象はBatchの非I/O・不変policy `MonitoringModePolicy` と閉enum DetailService。STANDARD/DEBUGのstrict外部値、詳細Actuator/Prometheus/Grafana/exporterの全一致、詳細保持15日/5GB（GBはSI=1,000,000,000 byte、GiBへ読み替えない）。STANDARD詳細保持0は基本監視/logの停止を意味しない。実serviceの状態採取・切替・配布・target起動、既Web/API管理HTTP、Root/nativeには接続しない。log levelの制御も受け付けず、監視modeとの混同を防ぐ。

通常PT事前判定=PT_DEFAULT。純粋なenum/MapとJava注入値のみ、実DB/VM/鍵/業務I/O/process操作0。Maven/JaCoCo/静的解析は自己所有の新only公開source snapshotで行い、選択suite以外のPTを実行しない。F03 Root11/未特定拒否操作は引き続きHOLD。元4222/common44成功の確認再演0。

| Test ID / method | 入力・操作 | 独立期待値・根拠 |
|---|---|---|
| PT-OPS-MONMODE-001 / monMode001 | strict2値parse、設定getter | DEBUG=true/15日/5000000000 byte、STANDARD=false/0/0。SS351表のliteral、Productionからexpected生成なし |
| 002 / monMode002 | DEBUG全true、STANDARD全false | 正常return、入力Map不変。基本監視やlog設定を変更するI/Oは存在しない |
| 003 / monMode003 | 各mode×4サービスの全16真偽組合せ | DEBUGはmask15のみ、STANDARDはmask0のみ正常。その他30組合せは固定CONFIG_DRIFT、独立bit真理値表 |
| 004 / monMode004 | 空Map、4各key欠落 | 全て固定CONFIG_DRIFT。不足をfalse補正して成功にしない |
| 005 / monMode005 | mode文字列null、Map/null key/null element | 明示non-null契約のNPE。catch正常化0、観測UNKNOWNをfalseへ補正0 |
| 006 / monMode006 | 空/大小文字別名/前後space/未知/秘密canary相当の合成文字列 | 固定CONFIG_INVALID、入力原値がmessageへ含まれない |
| 007 / monMode007 | 64独立callerで両mode検証・getter | 元literal結果、状態共有/変更なし、全Future成功。fixture executorはfinallyで終了し完了を確認、sleepなし |

すべて正常/境界/異常/null/欠落/未知/並行を上表へ対応。DB TX/再送/rollback/実I/O例外は対象非該当（純粋policyでその能力なし）。失敗・未実行・skipはPASSにしない。要求coverageは追加全physical classのline/method/class/branch各100%、enum生成分岐を恣意的除外しない。Java25/既Enforcer/NullAway/formatとSpotBugs/PMD/Checkstyleの結果・適用性を保存する。

実行command/OS/JDK/Maven/対象source・archive/終了code/XML/CRC/session/coverage/static/hashは後続1542とPG7000新onlymanifestへ保存。既4222/oldnativeの結果を新sourceへ合算しない。変更後の451全体検証triggerは完成単位/停止前に別に判断し、限定部品の成功を正式全体へ格上げしない。
