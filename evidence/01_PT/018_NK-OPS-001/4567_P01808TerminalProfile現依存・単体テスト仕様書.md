# P018-08.02 Terminal Profileの現依存による単体テスト仕様書

NK-OPS-001、SS343/354、SSC193/196/234、451。既存 NC196001～004 をTest本文・期待値そのままで実行する。対象は4件を含むTerminalNativeCoverageProfileTest全体。PG15281の歴史証拠とPG38334の依存差を照合。旧FixedNativeCoverageProfileTestの5件は変更されたCheckpointに参照を持たず、同一入力・同一byteを検証して参照する。

| Test ID | 操作と独立した期待値 |
|---|---|
| NC196001 | 固定2役、既定inactive、固定Unit文字列・directory・拒否、現在の試験JVMは予約オプションなしで採取経路へ入らない |
| NC196002 | literal JVM optionの未指定・null・重複・未知・拡張を拒否 |
| NC196003 | 固定owner名と旧4組のprofile pathを比較 |
| NC196004 | 代用agentとin-memory mapのみでbefore-exec拒否・terminalの一回採取・二回目拒否・GOLDEN bytesと副作用の回数を照合 |

入力はfixture記載の合成値。現在の試験プロセスが読むのは自身の起動オプション。サービス、OS所有、ネイティブ計測、原本、DB、遠隔環境の採取は別の受入条件。Linux/JDK25、strict Javac、既存静的規則、XML/execとCRCを独立照合。コマンド・source・UTC・終了値とTestIDは結果書とmanifest。
