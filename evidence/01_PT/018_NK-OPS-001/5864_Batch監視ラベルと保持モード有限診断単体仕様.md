# Batchの監視ラベルと保持モードの並行試験

NK-OPS-001、SS351・354、WBS-P018-09/2とWBS-C07、BUG-3928／YKT-2997。

| Test ID | ローカル合成入力 | 独立期待値 |
| --- | --- | --- |
| BATCHLABEL013 | 4 worker、64 caller。元fixture定義の六familyの手書き期待表を2つの別Policy instanceに入力。 | どちらも固定ラベル名と値の同じ組を返す。値取り違え・未終端0。Futureと所有停止は従来10秒。 |
| RETCONF007 | 8 worker、64 caller。DEBUGとSTANDARDを交互に供給。 | DEBUGは15日・5,000,000,000 byte、STANDARDは0日・0 byte。別modeの設定保持と元値の不変を判定。invokeAllと所有停止は従来10秒。 |

試験の本体と終了がともに失敗した場合、本体失敗を保持し停止失敗をsuppressedに記録する。共通補助の既済診断試験を参照し、同一の二件を正規Batch、固定Micrometer、JDK 25、元fixtureのcompiled scopeに対して選択する。保全manifestに選んだclass、XML、exit、未加工coverage、SDK、コマンドを記録する。実metric endpointやサービスの状態を使用しない。
