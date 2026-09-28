# 227 NK-OPS-001 固定Backup起動client PT仕様（PG352）

状態: Production外部起動に必要な限定境界の仕様。これ単独ではMorning親からの起動・backup成功・R2を受入しない。

| 項目 | 内容 |
|---|---|
| Program / class/method | NK-OPS-001 / `BackupUnitStartClient.create/start`、`Attempt.awaitClient/status` |
| 関連正本 | OPS-009、BAK-001、UI251、SS341§5/§6.1、SS343§6.15、SSC-092/093/105、BUG-315/YKT-248 |
| fixture | `RootStartupContextTest.Fixture`のMORNING identity、既存`InspectorUnitProbeFixture.Child`を限定注入。実`systemctl start`はHost PTで発行しない |
| 独立期待値 | SS341の固定Unit名`schubert-nk-backup.service`とsystemctl絶対argv、M/A/原本保持下の前提、起動clientの結果とworker receiptの厳密分離。Production methodでexpectedは生成しない |

| Test ID | 目的/入力・操作 | 期待・境界/異常 |
|---|---|---|
| PT-OPS-BSTART001 | 正しいMORNING root・固定policy・正常childで`start` | root→policy→root→固定`/usr/bin/systemctl --system --no-pager --no-ask-password --no-block start schubert-nk-backup.service`→root→root、stdin/stdout/stderr全close、client exit0のみ。worker成功は未判定 |
| PT-OPS-BSTART002 | 起動前のpolicy/root拒否、割込 | client起動0、既知拒否を保持。別Unit名/任意commandを引数として受けない |
| PT-OPS-BSTART003 | client exit非0 | `CLIENT_EXITED_NONZERO`、owner close、worker成功0 |
| PT-OPS-BSTART004 | timeout後に同handleを再照会 | `UNKNOWN`でlive childをdestroyしない。再試行後のreapだけexit結果へ遷移 |
| PT-OPS-BSTART005 | stdin/stdout/stderr close・getter異常、null child、start呼出後IOException/Runtime/Error | 全て原因非露出`UNKNOWN`。handleなしは再照会してもUNKNOWN、poison後は成功に昇格しない |
| PT-OPS-BSTART006 | 待機中/直前/直後割込 | interrupt flag保全、UNKNOWN・自動kill0、flagを試験fixtureが解消した後だけ同handleで再照会可能 |
| PT-OPS-BSTART007 | factory null・別service・MORNING正規actorとnative start port | null不変条件、別service拒否。native portは無害な`/usr/bin/true`だけ実行し固定systemctl startを発行しない |
| PT-OPS-BSTART008 | 同じAttemptを再照会、policyの固定BACKUP target | terminal status単調、再spawn0、起動client exit0をUnit Invocation/全cgroup終端・両archive成功へ読み替えない |
| PT-OPS-BSTART009 | SSC106の固定intent portを追加し、公開成功/不明/起動client送達不明を注入 | root→policy→root→intent公開→固定clientの順。公開不明ならclient0件、client送達不明なら`UNKNOWN`でintentを自動retireしない。独立期待順序はSS341/343の先行保存契約から作る |

実行環境/command、対象commit、line/method/class/branch coverage、静的解析、実結果、BUG/SSC、sanitized evidence hashは[228](228_NK-OPS-001_Backup起動client_実行結果.md)に記録する。JSpecify `@NullMarked`、null注入負例、例外・close/割込・再照会を網羅する。start後UNKNOWNの親M/A保持とhard-timeout再起動barrierはこのclass単独では証明できず、親接続PT/実VMを別必須gateとする。
