# G13.07・残338 sourceの静的参照graph候補

2026-10-25 13:48 JST。source64446不変更、G13_COMPOSITE338_REFERENCE_GRAPH_V1、開始1/3/7pp、群cap10。fresh使用65/残35/reset1793382075。現在窓の残10%以下/取得不能以外の旧累計停止は不使用。

目的は未登録338（複合293/helper45）のうち、既存正常9246のclass bytesと元Main責任から一意な担当を確認できるsource候補を特定し、独立反証後に登録すること。候補数は未測定のため凍結時nullで、全338を埋める目標/推測は置かない。成功・不成功試験の再演、対象compile/ロード/初期化/メソッド/JUnit/Root/VM/DB/鍵/通信なし。公開source/既正常Jar・test-classesを静的に読むだけで、PTの代替実行や実測coverageではない。

固定入力は9246正常manifest989d9e91、現Main物理manifest9252/70f008f4、直近9374/0f2cfc89と旧941/943/485責任。test-classesは9358の固定全六tree hashを前後検証し、各sourceは現在/正常snapshot/正常入力hash一致を要求する。

ClassFileのCP Classとmember所有class、SourceFile/packageを構造解析し、Mainは実JarのSourceFileから正確なMain sourceへ束縛。Test helperを経由する参照はsource graphの固定点で依存Main所有の和集合を計算する。自source内参照を除き、未解決project class、重複class帰属、reflection/動的class名解決のあるsourceと依存者は未確定のまま。参照先WBS集合が厳密に一つで、手書き責任根拠と整合するものだけ登録候補とする。多担当は少数へ丸めず未確定を保持。class名/suffix/packageだけでownerを決めず、changeOwnerから費用を補填しない。

独立確認はJDK javap -v -pのClass/Methodref等とSourceFile/this_class metadata。raw disassembly/fixture値は保存せずSHAと許可したsymbolのみ。小さなliteral構造vector、文字列擬似class参照、reflection、graph cycle/unknown/multiple-owner反例、既ownerの保持を確認する。既Mainownerが一意でも全assertion/要件/終了依存の受入とはせず、source path primary責任候補の限定結果とする。候補と根拠を固定してから独立確認し、positive shape→cost一field等のcounterexampleを要求する。

成果はcandidate/UNKNOWNの有限一覧・独立post・必要な485486参照同期・計測。元941/歴史943・481/484/予算/正式1964-53/17-190/工数null/QA051final/全actual HOLDを変更しない。BUG1746全current auditHOLDをPASS化しない。群上限内で確定不能なら当該候補をHOLDし、他の許可済み独立PG/PTへ継続する。
