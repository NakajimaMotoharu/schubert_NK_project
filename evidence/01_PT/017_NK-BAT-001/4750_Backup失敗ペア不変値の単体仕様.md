# Backup失敗ペア不変値の単体仕様

NK-BAT-001、OPS-009・BAK-001、UI251、SS331 §8.3／SS341／SS343、SSC-055・124。WBS-P017-06。対象は `BackupFailureSnapshot` の構築・保持値・一般診断。借用ポートへ接続する別試験と区分する。

| Test ID | 固定入力・独立期待値 |
|---|---|
| PT-BAT-BFSVALUE001 | 同一run・同時刻開始・別IDの二step。終了＝開始と終了＞開始を受理。保持値、同値・異値と固定伏字を確認 |
| PT-BAT-BFSVALUE002 | DB側とconfig側のstep違い、ID同一、片側ずつのskipを単独に与える。五ケースとも同一の固定不整合診断 |
| PT-BAT-BFSVALUE003 | 別run、異なる開始、開始より前の終了。各一条件だけが異なり、固定不整合となる |
| PT-BAT-BFSVALUE004 | 必須参照三つを順にnull。終了をµs境界から1ns外す。不足参照は各境界で拒否し、精度不一致は固定時刻診断 |

既処理を実行して期待値を生成しない。正規Batchと同じ物理でconstructorを測定する。PG43914の既合成7件を当単一execに含める場合も、再実行を新規IDへ加算しない。
