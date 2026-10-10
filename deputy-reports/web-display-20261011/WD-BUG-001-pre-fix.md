# WD-BUG-001 (副担当ローカル、正式915採番待ち)

UI222§8は質問受付の更新POST送信buttonをclient-sideでdisabled表示する仕様。予約基点a39d95eの質問JSにはdisabled変更がなく、questions/new.htmlにも共通disabled handlerがない。3script/共通layoutの入口照合で別handlerなしを確認。独立期待値はP016-25.02-independent-expectations.json。正常質問のsubmitでbutton.disabled=true、invalid submit前のbuttonはfalseを維持し、修正後の明示submitでtrueとする。質問body/tokenやserver再送仕様は変更しない。

対象: P016-25.02/.03、question-input-validation.js と対応Node fixture。重要度:表示契約不一致、API二重送信防止の欠陥とは認定しない。修正前に専用Node fixtureへbutton state期待を追加し、失敗を採取する。正式915/916と既存品質台帳の反映は主担当へ委任。今時点でProduction未修正・実再現未実行。
