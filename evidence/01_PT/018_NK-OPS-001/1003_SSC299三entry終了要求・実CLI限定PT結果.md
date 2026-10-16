# 1003 SSC299 三entry終了要求・実CLI 限定PT結果

1002仕様、**PG4690元45091 actualMaven0/qualification0、78PT/16suite、全class/method XML inventory一致・F/E/S0・not-run0**。固定source snapshot `825e463334c43a5bc96f50db964df22e11758d1b`、Java25.0.4/Maven3.9.12/Python3.14.4/Linux、dev-foundation、2026-10-16 20:24:52.265744～20:26:06.742607Z（74.476863秒）。実command=1002の4690 runner。元Main不帰還probe問題をcoverage除外/終了抑制/bytecode改変で処理せず、main同bodyのデータ/制御portと別真正JDK25 CLIを検証した。

| 実main | line covered/missed | method covered/missed | branch covered/missed |
|---|---:|---:|---:|
| RootServiceLauncher.main | 11/0 | 1/0 | 8/0 |
| MorningProcessMain.main | 2/0 | 1/0 | 命令なし |
| CleanupProcessMain.main | 6/0 | 1/0 | 4/0 |

proof35line/1method/14branch、environment9line/1methodも各miss0。八port試験はtyped終了0/10の帰還順序、既IO30/argv70、unknown/fatal/null/測定失敗の非正規化・終了要求非発行、同測定Optional identity、native noargだけ公開・package ports非公開、Test thread handler復元を確認。別ExternalEntryRejectionTestのchild JVMは同FQCN/既argvで期待70/30・空出力・生成物なしを維持した。実VM/Unit/DB/Root/noargs業務・有効resume/ADMIN/Backupは発行0。データfixtureはnative成功/stream資格へ加点0。

Maven log SHA `02c253fc56bbfc16374d16856afda973866ae292c59d45b9931026b6d2774980`。MainTerminationPortTest XML SHA `fc56d5f13313d2be62711eb5648c7f8924d42134f1c525832e566263ef76eea8`、ExternalEntryRejectionTest XML SHA `17926171983ecce82fc1dbed2f53ac7ad0d1f4be290beeee18ed1a60900b29a2`。全入力/元owner/command/終了値/全16XML/hash/coverageはPG379/pg4690-entry-termination-selected-v1に保存。原PG4684の43PT機能成功/coverage資格1は別保全し書き戻さない。

selected実class byteは**1646 Main、旧1644から1638同byte・既6物理class変更・内部interface2追加・削除0**。変更は三entry family（RootServiceLauncher/$1、MorningProcessMain/$1/$Archive、CleanupProcessMain）だけ。新Measurement/NativeAdmissionは抽象宣言で、対象Javaのcoverage除外を増やしていない。残全体/署名/native/F03/CHR/451は未受入、旧964e native9を候補へ合算しない。

次のfresh全体は**期待**3739PT/549suite/1646Main（旧3721の全identity＋手書き追加18case・新四suite、旧method名/ID保持）と明示し、実完走/独立XML/全Main/hash/静的確認まで合格としない。候補825eは未配備、現配備964e/PG4432の正規停止後状態を保持する。正式1964/53・工数null・QA051finalは不変更。
