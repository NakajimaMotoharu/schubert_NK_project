# NK-BAT-001 backup_manifest値単体テスト仕様書

## Coverage集計とcompiler生成methodの独立確認

[JaCoCo標準filterの定義](https://www.jacoco.org/jacoco/trunk/doc/changes.html)（record accessorは0.8.9、生成equals/hashCode/toStringは0.8.6から集計対象外）。本scopeはJDK25 javac生成のBackupFileDigestのsize/sha256、BackupVersionsの全8 accessor、BackupManifestの全9 accessorと各生成equals/hashCodeが標準filter対象。理由はconstructorで確立したcomponentの単純読取・JDK生成値比較であり、新たな除外設定や業務分岐の除外ではない。手書constructor/guard/全計数・名前・codec・redaction toStringはすべてJaCoCo計測対象（新4class/18method/134line/50branch missed0）。

計測外componentもBAT178/180/184・BAT187で独立literalの全19 accessor値を検証し、BAT184で同値/変化したmanifest・hashCode整合を確認する。NULL/範囲/相互不変条件・所有/並行は別Test IDで全実行。18methodというレポート値をclassfile上の全method総数と同一視しない。内部review: 当該3recordは可変componentなし、生成accessorに業務分岐なし、手書toStringはredaction期待を別確認、要求の正常/境界/null/全業務分岐を損なわないと確認。全Programの同種標準filter説明の最終棚卸しは451/後続総合品質gateで維持する。

実装・探索段階へ移行。BAT182のAsia/Tokyo歴史oracleはBUG182/YKT143先行9447f481、037のIANA独立offset/遷移literalを使用する。全9field null・7token/schema各境界、全step種別・id/run/skipped/開始整合、µs/上限/overflow/64並行を検証する。最新結果は034。正式認定前のため以下の起票時状態へ合格件数を遡及しない。

PG165/SSC058先行8a606fc7、BAK001～008/BKO001～008/UI251 §5/SS311・341 §6.4・343 §5.3。PG164正式08のsource凍結中に仕様のみ先行、未実装/未実行/認定0。

| Test ID | class/method | 目的・事前条件/入力/操作・独立期待値 |
|---|---|---|
| PT-BAT-178 | BackupManifestValuesTest.completeIdentityAndDirectoryName | 公開固定run/DB90000・CONFIG90001/3file1・512・200byteから独立JST名と713合計・712config量 |
| PT-BAT-179 | BackupManifestValuesTest.fileDigestBoundsAndOverflow | size1/MAX/0/負値/hex長さ・大文字/合計overflow、既定3fileだけ |
| PT-BAT-180 | BackupManifestValuesTest.versionTokenBoundaries | 8version scalarの1/128境界・不正byte・schema001/999/000 |
| PT-BAT-181 | BackupManifestValuesTest.stepAndRunBinding | DB/CONFIG取り違え・id重複・同一run/別cutoff・skip・attempt別番号許容 |
| PT-BAT-182 | BackupManifestValuesTest.timeAndPrecisionBoundaries | UTC0001/1582/9999・JST年境界・µs/順序・内容生成終了とstep開始 |
| PT-BAT-183 | BackupManifestValuesTest.nullAndRedaction | 全constructor/null/固定redacted診断・値を例外へ出さない |
| PT-BAT-184 | BackupManifestValuesTest.immutableAccessors | 全record accessor・同値/hashCode/別値と元オブジェクトの独立性 |
| PT-BAT-185 | BackupManifestValuesTest.concurrentValueUse | 64並行model利用・値計数/名前が相互混在しない |

Fixtureは公開合成run/id/version/count/hashだけ。サイズ/hashは申告値のvalidation fixtureでありactual dump成功の証明ではない。golden JSONはSS順・literal fieldから独立作成しProductionでexpectedを生成しない。PK/実DB state/実artifactのI/O・hash/暗号・復元・7世代は別未完了。全正常/境界/異常/例外/NULL/未知/所有/64並行を上記Test IDへ一意に対応付ける。

Production全class/method（record accessorを含む）: BackupFileDigest constructor/toString、BackupVersions constructor/全field検証/toString、BackupManifest constructor/run/directoryName/configurationBytes/totalBytes/time/toString。line/method/class/branch100%・NullAway/negative・SpotBugs/Spotless成功が必要、除外や無意味assertionで代替しない。障害は修正前915、共通原因916、設計はSSC058を先行する。

実行環境は421 Java25/Maven、コマンドは該当batch -am test/正式clean verify。034_NK-BAT-001_backup_manifest値_実行結果.mdとmanifestへ日時・OS/tool/branch/対象commit/実行command/exit/input/期待と実際/4coverage/static/BUG・SSC/証跡path・hashを記録する。未実行/skipped/flaky/error/failedは合格にしない。
