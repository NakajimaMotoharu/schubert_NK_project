# NK-OPS-001 API設定読取結線実行結果

PG276/PT-OPS-API-LOAD-001～004。選択4PTはfailure/error/skipped0。Java25.0.4/Maven wrapper、branch `dev-foundation`。選択run単独は正式認定に算入しない。

正式`PT-WEB-20260925-14`、source `4eeb1d7e5a47ad3bb5d286dcd7e10bbedcb63b48`、2026-09-25 05:17:19～05:29:52 JST、command `sh tools/quality/030_run_pgpt_verify.sh PT-WEB-20260925-14`、exit0。全1,924PT（CHR41/Protocol80/Storage92/API762/Web545/Batch404）failure/error/skipped0。Production Java6 module instruction/branch/line/method/class missed0、SpotBugs0、019負canary103/103、018全53scope/保存hash再照合PASS。root manifest SHA-256 `dca1c2d0d819076713ad37c1d64f7f3a063cd32d09681ae5642695aacd032091`。API4件は全PASS、入力/独立期待値は066、実際のTest ID→method、coverage、環境、関連番号、sanitized evidence path/hashは同Program `evidence/manifest.json`と`results.xml`。公開非秘密fixtureのみで、実`/etc`/credential・外部main・DB/JMS/実NK CHRは未認定。
