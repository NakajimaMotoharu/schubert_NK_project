# CleanupStepとExpiryAuditの現正規JAR単体試験仕様・結果

候補 `44e32a2211d35b950f75c8095ac6736d467a918a`、dev-foundation、Java 25.0.4、JUnit 1.13.4、JaCoCo 0.8.15。NK-BAT-001、OPS-009／UI251、SS331 §8.3、SS332 PG181／SSC310、SS341、WBS-P004-05／P017-11／F03、YKT-2864。通常JARと現fixtureの実使用閉包を固定して実行。全Test名・command・元XML／exec・静的由来・CRCはmanifestの証拠を参照する。

| 試験群 | 独立した合成入力と期待 | 結果 |
|---|---|---|
| PG42956／CleanupStepPortTest 10件、CLNPORT010を含む | 借用Connectionと固定SQL・typed bind、0/1/1000境界、既知／未知件数、欠落・null・未知、順序、必要時だけ一回ずつclose。独立固定SQL文字列、型と値、5箇所×3経路の順序表、例外同一性 | 10成功、F/E/S・未実行0。対象1クラスの無フィルター L75/M7/C1/B28/I325すべて不足0 |
| PG42958／ExpiryAuditの五fixture 31件、EXPPORT-J011を含む | 合成JDK Proxy／Guard callback、11列と16bind、日付・UTC、stage/finish再送一致、欠落・null・不正組、lost ownerの観測結果、取得順と解放、SQL固定診断・fatal例外同一性。固定独立期待値、borrowed commit/closeなし。EnumSource 8件を含む | 31成功、F/E/S・未実行0。対象7物理中実行4のL284/M52/C4/B190/I1416各不足0。抽象3型の実行可能コードは0。証跡を除外しない |

PG42956 manifest SHA-256 `e853ce2bafd3b282181e4a4aa3742352ff7d710681ff776146248c9fde9583f3`。PG42958 manifest SHA-256 `2dbc7d341290db82c16dddb8e01c502d1adcb21fd6eddbac66f30a89361d8cf8`。候補の異なる旧全18／30や旧追加1を合算しない。実削除、実DB、実所有、保持原本、F02/F03終了依存・451正式判定は未実証。
