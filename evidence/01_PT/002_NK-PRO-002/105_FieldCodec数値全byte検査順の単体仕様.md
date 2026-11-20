# FieldCodec数値全byte検査順の単体仕様

NK-PRO-002、WBS-P002-01/2、RD MSG-004、UI232、SS322 §6.2。対象は`FieldCodec.decodeNumeric`。文字の妥当性を全byteで先に検査する詳細設計を、単独の桁あふれ・文字不正と区別して確認する。

| Test ID | 独立した入力 | 独立期待値 |
|---|---|---|
| PT-PRO-002-N03 | 十進`9223372036854775808`の直後に`0x2b`または`0xff`を置いた各20 bytes。許容範囲0～JDK signed long最大。 | SS322 §6.2のASCII 0x30～0x39全byte先行検査により`PermanentProtocolException`、非数字の固定診断、演算例外causeなし、入力保持。 |

上限を示す十進定数と固定不正byteを試験側で指定する。既N01～N02／EXC-001の正常、桁あふれ、大域上限、null、符号、fillerを元期待のまま保持する。通常Protocolだけを再資格し、実配信／JMS／DBを扱わない。コマンド、環境、source、終了値、XMLと計測のSHAは結果manifestに記録する。
