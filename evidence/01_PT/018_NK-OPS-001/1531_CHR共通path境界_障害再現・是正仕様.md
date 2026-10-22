# 1531 共通harness path境界 障害再現・是正仕様

2026-10-23、BUG1640/YKT1393、既WBS-P020-01.01群1779内の追加発見/是正。元群参考.5/1.33/3ppと上限10ppを変更しない。原計画成果と追加障害の手戻り/工具是正を分け、旧41成功/旧16SpotBugsを新sourceへ加算しない。Root11/actualHOLDを解除しない。

対象はcommon GateCliのpath契約だけ。filesystem rootを表すPathはgetParent/getFileNameがnullであり、absolute normalizeだけでnullが無くならない。既原41の四100は入力を網羅したことを意味せず、静的16中の実未検査三経路を個別是正する。Main修正前に台帳へ起票済み。

## 独立Test ID・期待値

| ID | 入力/操作 | 独立期待値/副作用 |
|---|---|---|
| PT-CHR-PATH-001 | 既preflightFixtureのcurrent/users/log/runtime等は全て新TempDirへ固定、pgLogだけ親無しPathの文字列。preflightを呼ぶ | IllegalArgumentException、messageは契約違反。NPE正常化/catchなし。元baseline変更0、VM/DB接続0 |
| PT-CHR-PATH-002 | writeJsonにparent無しPathと固定emptyMap | IllegalArgumentException。ACTIVE_OUTPUTSへ追加/temporary作成前に拒否、原baseline変更0。REDは新snapshot cwdでnull.part不在を前提確認し、既残置を削除しない |
| PT-CHR-PATH-003 | guard是正後、promoteCurrentにnull又は名前無しPath、新TempDir baseline | IOより前にIllegalArgumentException、baseline未作成。未修正実装でfixture外参照を発生させないため本経路のREDは未実行と明記 |

REDは001/002を新Testへ追加しMainを元byteのまま、新only隔離runで他正常41も併走する。001/002が期待契約例外ではなくNPEで失敗することを元XMLから確認後、同Test期待値を変えずguard是正する。003は同時に安全guard後の独立negativeとして追加する。旧APIのNPEを正常結果へ変更せず、assertThrows(IllegalArgumentException)で検査する。

修正は三guardを副作用前に置き、正常なpath/24catalog/DIF/出力/baseline/原子性を変更しない。source/Testは単一群で固定し、選択五suiteの全common PT＋JaCoCo四100・必要lint/null/静的を再資格化する。Production src/POM/gatesはe7原4222と同byteを保ち、common source/Testだけの変更を原全体成功の流用や新全体正式認定としない。
