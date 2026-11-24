# 音楽ペアの既定locale互換単体仕様

NK-MIG-001／MIG-DAT-004・005、MIG-003／005／006、UI223／242／243／254、承認SS343のMusicMigrationPairing、WBS-P019-03.02/2。Test IDはPT-MIG-MUSICPAIR027。

合成の役割判定入力はtheme.flac＝THEME、theme_inst.flac＝THEME INSTRUMENTAL。実体ファイルは参照しない。

| JVM既定値 | 独立した期待値 |
|---|---|
| en-US | 大文字Iをiとしてinstに一致。key theme、Mainはtheme.flac、Instrumentalはtheme_inst.flac、shadowなし。 |
| tr-TR | 大文字Iをドットなしの小文字ıとしてinstに不一致。表示名の固定正規表現では両方がtheme。先に来るtheme.flacを後者が上書きし、Mainのみtheme_inst.flac、shadowにtheme.flac。 |

期待値はSS343の既定locale参照、固定regexとpathのbyte順（点が下線より先）を別々に適用した手計算。JUnitでJVM内設定を隔離し、正常・例外ともdefaultと両Categoryを元に戻す。OS設定、現ファイル、V029保存、DB、実Current比較は含めず、既存26個別試験の結果を再実行しない。
