# REQUEST responseBytes 独立原再現とPG是正

BUG2273/YKT2018をc473f8で修正前起票。SS351§3.3ではoptional responseBytesは存在時の整数0..999999999999。期待/DB/witness全部同値であっても型/値域不正を許容しない。Currentの旧null rowを変換せず、全new REQUESTだけの契約として実装する。

PG18688は旧186fa正常jarに新CorrelatedLogHttpNumberTest全2methodだけを実行。a8a374実exit1、2case/1failure/error0/skip0。assertAll内に複数同値不正を集約、元ログ/XMLと旧Mainを保全。原expected-redをPASSに算入しない。公開証拠は020/evidence/PG18688-response-bytes-original-red-v1。

PG修正はnew REQUEST present responseBytesをunsignedN12で検査し、既存elapsedMsのisIntegral/canConvertToLong/0..999999999999を同じhelperへ等価移動。optional missingを有効、present null/boolean/text/fraction/floating/negative/N12超過/Long超過を無効。旧before/after既知nullは不変保存。SS/UI/DB/wire/Core b093とCurrent baseline変更0。

PG18690/30870 55d088はformat/package/testCompile全0、Main5/Test5（新全24）のimmutable snapshotと正常jarを保存。Test015はcurrent/nk全stageで20不正literal、016はmissing/0/1/maxとoldnull保存。静的PG18692は観測中、green24未実行。source固定→同source正常24/全9physical/source counter/単exec・独立postが必要。元186fa22を新sourceへ合算0。

同705群原.75/2/6 cap10不変更、共有差1暫定・専有/N-Tnull、新S/V予算なし。usage10:08:28/e0cdd9…/offset3028089255、次11:08:28以降。全HOLD/正式1964PT53scope/歴史17/190/工数null/新leaf0を維持する。
