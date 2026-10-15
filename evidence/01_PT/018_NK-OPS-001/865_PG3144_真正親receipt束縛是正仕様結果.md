# PG3144 真正親receipt束縛是正・仕様結果

## 障害と保全

BUG1267/YKT1033、SS343/353/451、関連864・WBS-N05/N14。05d8302caの3122（exec56951）01:42:45.393742～47.113889Zはactual1/sourceQualifiedtrue、payloaddf8f2eab85efd95bd4540fdf4eaa17d9c15006a6e9205aa9e9a39298e64bf08f。line56の`completed`が旧2890 headerと当3034 sealed parent rows/doneのactivation不一致を正しく拒否した。

誤ったpositiveは74729/INVd419/Job11471、正しい直前genuineは0ac69/INV65ad/Job35795/start18100986959。guard/新guest slot/Native copy/Scope/Root commandより前であり、失敗をDONEや成功に読み替えない。fresh SSH ROでboot79a、3122guest slot不存在、Root MainPID/ControlPID/Job0、当zz3100の644byte/hashabe8732d不変を確認。旧host slot/payload/1/log/immutable observerは保存し、3122を再実行しない。M/A/DB保持scope生成前なので回収/強制unlock/stopは不要。

## 是正と独立反例

現在3106 actual postのtoolHashesが封印する `pg3034_parent_receipt.py` SHA834d0b3d6d4ad5eb656e69f89e60e969d9586dc7d2932435ebdfe49d9c604c1dと同byteだけを使用する。ASTで最上位RECEIPT assignmentだけを交換し、埋込された歴史的拒否/退役oracle等のtupleは一括置換しない。実genuine3034と3006のreceipt bytesが同値であることも確認した。

一回startの保存先は新-only `pg3144-current-parent-receipt-resume-once-v1`。既準備runtime/既observer3120を再使用し、prepare/reload/observer stage/watchを二重発行しない。新3124/3132/3134のconsumerとnative16 copy元を当slotへ接続。3138 readyはnew-only v2とし、旧v1 class/input/資格を保存する。Production Main/3691全回帰/native18/署名/配備不変更。

`pg3122_prepared_browser_resume_contract_test.py` 四試験actual0：当BINDING七項目を独立literalで確認し、固定NKDONE1/10とPID1 job/success二行を実分類して正常を確認。旧headerでは同fixtureを拒否し、run/cutoff/activation/boot/invocation/job/start各一fieldの外国値を拒否する。既三試験（全11/native16/唯一start/元1800秒/正規resume）も維持。`pg3134_browser_resume_contract_test.py` 全三actual0、新slot/観測窓/四ordinary/SOCKS前後guardと歴史activation拒否を維持する。

## 次の実再試験

clean commit→3138 v2全六phase（Java warning0/pure独立/三Python suite/当credential RO）→同3120 observer現在frame/所有をfresh確認→3122工具の新3144 slotを一回だけ実行→3124新tuple→真正terminal/全24/seal→普通owner維持の全Browser十二case/全24→最後にownedstop/native。新Rootは現時点未発行。BUG/YKT完了日はactual new consumer成功と関連全対象の確認後に記入する。

## 実再試験（起動前consumer範囲）

9ff4c091f固定、3138v2/exec73287全六phase実0/sourceQualifiedtrue。既3120 immutable observer/exec80095の現在quiescenceを再確認し、新3144/exec49861は01:47:40.765076～52.092912Z、actual0/sourceQualifiedtrue、payload7743dbf49a281f61d912df319c338209bd85bed7b15e2a7505f28736a1d41f5f。全187/全24/原本/Backup/native16/11項目/直前genuineの束縛を通過し、当新slotへdurable予約・native16保全後に唯一start発行。新Job60559/INV2449cff7ecf946e882f23e6bde8c41d0/Root225062/start28121423183。

3124/exec06d34f実0、01:48:14Z、activation323bc9ad-1528-449a-8067-19228ee1e046/run0dc/cutoff元値・Root225062/t2812142/argv56023186をfresh実捕捉。元1800秒不変更。BUG1267/YKT1033の有限consumer/header範囲は修正9ff4c091fと本actualで完了2026-10-15。新親処理はRUNNINGで、真正DONE/ordinary/Browser/全24終端/native/正式受入へは加算しない。旧3122の1は保持し、成功へ置換しない。
