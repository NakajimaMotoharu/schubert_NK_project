# 1210 JMS受信rollback未確認：修正前結果

1208/BUG1489/YKT1249、Main2bbb不変更。red-api-v1 sourcea45b6c0be/元39121はtestCompile不成立（BUG1490/YKT1250）。依存七件五suite成功だけで、新API三/Web一はnot-run。空counterのtargetFour100=trueは無効な工具値として不採用、元manifestを書き換えない。

fixture二lambda/SAMと赤・空counter判定をbe808453aで是正、red-api-v2/元23630はactual1、01:18:46.390304Z→01:20:19.990993Z/archive `0bea5d8ca2ab7c7eb4a04612cfe890af2d0e309a94421b11d23336fb944f0e69`。10件6suiteのうち新UNC001～003だけが予定assert failure（ready維持/fatal未通知）で、sourceFixed=true・目的red=true。全849Main sourceは2bbb同一、実1349Mainは旧whole同byte、Web315はMavenのAPI test依存で未build/未試験。失敗三件をPASSへ加算せず、原API再現は再演しない。

次は未実施Webだけ`pg5794_rollback_unconfirmed_selected.py red-web`、APIは既catalog一件を使い依存失敗を避ける。未実施を迂回や拒否PT代替にしない。Webの予定独立失敗と全1664同byteの照合後にPG-D441の是正へ進む。現時点BUG1489/1490とYKT1249/1250はOPEN、修正前の二run/ログ/XML/hashは私有workの一意pathで保持する。正式1964/53・17/190・QA051final/実所有HOLD不変更。
