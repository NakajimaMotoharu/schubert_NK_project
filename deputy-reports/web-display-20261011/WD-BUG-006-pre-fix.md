# WD-BUG-006 (副担当ローカル、正式915採番待ち)

UI222§5/SS313§10、UI225§4はUsername/初期Password/Password確認/Role/有効を必須とする。user-new.htmlのlabelに必須表示がなく、Role/有効にrequiredがない。validation-summaryもli textだけでanchorがない。対象P016-16 templateに固定id・label for・必須表示・required・summary linkを補う。password値を再表示せず、既存GET/POST/token/error/戻り先は維持する。操作後client-disabledは別外部JS追加が必要で、許可3JSの単一質問scriptを他画面へ流用せず未達として主担当へ残す。
