# BUG-3276／3277 API custom metric payload有限終了の結果

Core `bcc9e0673287c51950ecab9b36350abfcd4b2c69`、固定試験 `dece06244977095fcf87245f2050dc5a507d94bf`。PG39392の元26はすべて初回成功、失敗・error・skip・未実行0。APIPAY013、APIFULL011/012の3 worker fixtureを期限と終了後解放へ揃え、元assertion 15 をtokenで個別照合。APIFULL004に同hash異値2とCONFIG_INVALID固定期待を加え、供給0／標準read0を保持。Main差0。

先行静的PG39388の旧013をBUG3277へ起票し、必要再コンパイル後PG39389は静的適用0・PMD生19。独立PG39396は物理26・正CRC18、全物理26は前の同型と同byte。PG39400は本体生14L/3M/1C/16B/94I全到達、支援生278箇所の未到達を保存。F03/451全体や実metric sinkへ転記しない。

Linux amd64、JDK25.0.4／Maven3.9.12／Micrometer1.17.1／Prometheus1.7.0、dev-foundation。[独立証跡](evidence/PG39400-f03-api-custom-payload-finite-independent-v1/manifest.json) SHA-256 `71d1194bd1bf71025ba8a5de40c17a50c98e5c897d50cf69ab5debcac072ba0d`。実環境command、exit、XML、CRC、静的、生counterを参照できる。
