# WebSessionRowの時刻・保持値境界の単体仕様

NK-WEB-001／NK-AUT-001、RD FUN-001／AUT-001～004、UI226・242、SS314 §7.2.3／SS331 §9.1／SS352、SSC-040、DDL V003の `ck_web_http_sessions_max_inactive`、版・時刻制約。WBS-P015-01の局所通常試験。

| Test ID | 合成入力 | 独立期待値 |
|---|---|---|
| PT-WEB-ROW001 | created=last=expires、1秒、版0、次に時刻昇順・28800秒・版999999999 | 両端を受理。入力の参照、時刻、秒、版を保持 |
| PT-WEB-ROW002 | lastとexpiryのµs端を各1ns外す。created＞last、last＞expiryを独立に渡す | 4ケースすべて固定メタデータ診断 |
| PT-WEB-ROW003 | 秒0／28801、版-1／1000000000 | 秒不正と版不正の診断を区別し、いずれも拒否 |
| PT-WEB-ROW004 | identity、payload、last、expiryを一つずつnull | 各fieldの明示null契約で境界拒否 |
| PT-WEB-ROW005 | 同じデータを持つ二値、版が異なる一値 | 同値とhashの一致、相違版は非等価、一般診断は固定伏字 |

期待値は承認済み詳細設計とDDLから読み取る。合成の固定時刻・値だけを保持し、実sessionやDB読み書き、暗号化、外部通信、保存期限切れの業務動作へ接続しない。現sourceと単一execで対象物理四指標を確認する。
