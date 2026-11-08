# 内部transaction五method独立oracle対応 結果

仕様3841/scope625。Main7aed不変更、元23476九成功/独立23478再実行0。PG24052 Source/metadata check exit0、五method/元九Test ID/25assertion snippet/承認SSへ明示対応。

|method|元PT-JMS-TXP-|独立期待の範囲|
|---|---|---|
|constructor|001～009|二event route、null四依存/全非event destination拒否と提供依存構築|
|public onMessage|001/003/004/006/007|既no-op observerで成功/NULL/session/checked例外/提供隔離へ委譲|
|observer onMessage|003/004/005/008/009|null/session、失敗段階とchecked/Runtime identity、確認済と未確認rollback callback順|
|lambda$static$0|004|legacy failure時の既no-op callback。元run-level method coverageを参照|
|clinit|001～009|static callback設定との関連。最初の起動caseの特定は不可、各case別probe測定はない|

元golden literal/SS321 transaction・DLQ十property/SS322323 layout、case別body-read/sequence・same object/suppressionが根拠。009は通常/隔離どちらもrollback一回・confirmed無しを具体的リストで確認し、UNKNOWNを成功へ読み替えていない。006/008の送信は提供メモリJMSProducer callbackであり実brokerやcohort復旧ではない。

元四counter L41/M5/C1/B6 miss0は当全一Source/一physicalの元run実測。今回のmethod/case linkをcase別coverage、callee全域/DLQ sender/直接Error全graph・実環境・全G13/451受入へ拡張しない。元Sourceとclass SHA、descriptor、要求/SS/Test ID/独立期待・限界はmethod-oracle-relations.json。class初期化の正確な最初のcaseはUNKNOWNを維持する。過去のwrapper/authenticatorのlinkもcase別probeの実測を意味せず、既run-level coverageの範囲を保つ。

新PT/compile/JVM/JMS callback/実backend0、新BUG0。unique517/候補114/pending12/whole暫定93/正式1964PT53scope/newleaf0/工数null/G07未分類3313+22actualSecretCountnull/全HOLD保持。command `python3 -B evidence/01_PT/018_NK-OPS-001/input/627_transaction_method_oracle_review.py`、日時 2026-11-08T15:52:12.114862+09:00、manifest `evidence/01_PT/018_NK-OPS-001/evidence/PG24052-transaction-five-method-oracle-review-v1/manifest.json` SHA256 `691f686bfc07c045b4c883e87d91ef452c16adc960614a468ff43188068a11c6`。工具派生は明示contextの変更だけで、regexの一律数字置換は行っていない。Source固定/pushはPG24054 publisher参照。
