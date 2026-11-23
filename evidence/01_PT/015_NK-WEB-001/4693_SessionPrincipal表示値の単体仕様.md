# SessionPrincipal表示値の単体仕様

NK-WEB-001、NK-AUT-001。対象は `SessionPrincipal` の公開コンストラクタと値の公開契約。RD FUN-001、AUT-001～004、UI226、SS314 §7.2.1・§7.2.5、SSC-038・043。WBS-P015-01のF03局所証拠。

| Test ID | 操作・fixture | 独立期待値 |
|---|---|---|
| PT-WEB-PRINCIPAL001 | 分解形の e と U+0301 を32組、合成のrole/context/UTC時刻で生成 | NFCの U+00E9 32文字。UTF-8で64 byteに収まり、role・context・時刻の値を保持 |
| PT-WEB-PRINCIPAL002 | 空、孤立surrogate、65 byte、末尾ASCII空白、内部制御文字を個別に渡す | 全入力を `IllegalArgumentException` と固定診断で拒否 |
| PT-WEB-PRINCIPAL003 | 名前・role・context・時刻を一つずつnullに置換 | 各必須値の境界で明示的に拒否し、対象fieldの固定診断 |
| PT-WEB-PRINCIPAL004 | 固定の表示名を持つ合成値で `getName`・`username`・`toString` を取得 | UIとframeworkの名前は固定入力。診断は `SessionPrincipal[REDACTED]` |
| PT-WEB-PRINCIPAL005 | 同一の全fieldを持つ二値とroleの異なる一値を比較 | 同値のハッシュ同一、roleが異なる値は非等価 |

正規Protocol JARと固定sourceの単体JVMで実行する。入力は文書化した合成値に限る。認証、保存、通信、更新、再送の結果は後続の該当契約で検証する。
