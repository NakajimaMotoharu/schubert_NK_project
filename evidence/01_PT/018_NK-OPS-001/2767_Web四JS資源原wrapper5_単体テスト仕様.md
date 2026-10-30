# Web四JS資源・原Java wrapper5/Node30仕様

2026-10-30、主P016-25.03/関連P016-25.02追加0、着手前1/4/7pp、source6b53/normal14216。四Main JS136行/四CJS450行/四Java wrapper全5methodを全body審査、元のまま実行する。UI222～225/SS313/314/352、BUG1222/YKT988/PT-WEB-OPSJS2646、PT-SCR025/PT-SCR092/PT-QST-JS001。

|production JS|原Java whole wrapper|原Node subcases/独立oracle|
|---|---|---|
|search-speaker-submit.js|ScenarioSearchScriptTest1|8（A～H）：固定DOM欠落/イベント登録、ASCII 256/128/256境界、Unicode/NFC/Java trimの手算byte、全不正停止、修正後送信、game changeのrequestSubmit。|
|log-search-validation.js|LogSearchScriptTest1|8：固定DOM、256/64/256byte・不正surrogate/control・NFC/ASCII trim/Unicode手算、全不正停止/修正送信。|
|question-input-validation.js|QuestionInputScriptTest1|8：必須DOM、固定4096 byte残数/1～4096境界/NFC/Unicode/control/trailing ASCII、元文字非変更、送信時再validation/disable。|
|operation-post-submit.js|OperationPostScriptTest2|Node6：固定form/token/button、invalid→correct、valid disable/二重submit拒否/二form独立。もう一Java methodは承認四update templateにだけscript/form/operation_token/POST属性が一個、他三templateには無いことを検証。|

期待message/byte上限/残数/DOM回数/Node IDは原CJSの固定literalと手計算から作り、production JSからexpected生成しない。Node30はJava wrapper5の子試験で、異なる階層を単純加算しない。並行/再送観点はoperationの独立form/二重submit阻止（実業務再送ではない）、その他pure input validationに外側並行契約を推定しない。

Nodeのvm realmは固定document/TextEncoder/TextDecoderイベントdoubleだけで、fetch/ネットワーク/実Browser/VM操作なし。CJSはown copyのproduction JSを一file読取、user tokenはPUBLIC_TEST_ONLYという公開合成値だけ。Java wrapperは固定絶対Node24.19.0/version/syntax/coverage test、各child wait30秒/finally descendants停止、出力は新own target。Node binary sha bc17c508ffeed0ec622934f9b7fa72f8e78da65350e63c3eceb56fa688aa5e12。

normal input/Snapshot/現ファイルの四JS・四CJS・七HTMLを一致させ、Main11資源はweb Jarとも一致を確認。新onlySLOTに同一byteでコピーし、原Main/Test/fixtureを変更しない。新Java Main Source資格は0、Java class/branch coverageに0/0の合格を捏造しない。Node V8のline/function/branch各100を各実TAP/Node終了0/coverage threshold flagsから独立検証する。

command `PYTHONPATH=tools/quality python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14778_web_four_script_resources_pt.py`、後続14780/82 resource専用post。原JUnit5/4suite F/E/S/not-run0、各Node8/6/8/8 F/E/S/todo/cancelled0、四資源の非空coverageを確認。manifestに日時/branch/source/commit/command/exit/OS-JDK-Node/hash/全input・expected IDs/実XML-TAP/coverage・traceを記録、結果2768。正式1964-53/歴史17-190/工数null/QA051final/全HOLD・実Browser/CHR未受入を維持。
