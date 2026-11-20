# ProtocolのJava直列化依存監査

WBS-F02-a、RD SYS-011、UI211、SS311 §10。BUG-3395／YKT-2726。明示禁止の直接型依存を静的に点検する。

PT-F02-OBJECT-SERIAL-001〜007は、型名を固定したfield宣言でJava直列化のmarker、stream、descriptor、filter、失敗型を一辺ずつ報告する。008〜010は一般のIOExceptionとDataInputStream、別moduleでのObjectOutputStreamが当Protocol規則の対象外であることを確認する。Java 25／ArchUnit 1.4.2の合成fixture。オブジェクト直列化の実行や入力payloadは不要。

元は3/10、修正 `447a019ff2` 後は10/10と旧72/72。合成122物理で意図した53指摘だけ。別に現実Protocol JARの176物理を旧型付き入力とSHAで照合し、2,595型依存行に対象辺0（7物理は出辺報告なし）。[PG40634](evidence/PG40634-f02-protocol-serialization-independent-v1/manifest.json)

全六artifact、451、正式受入は別依存。
