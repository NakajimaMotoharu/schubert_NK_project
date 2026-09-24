# NK-OPS-001 service credential set単体テスト仕様書

Program `NK-OPS-001`、PG284/SSC-081。対象 `ServiceCredentialSet.load/copyPassword/copyKey/version/close`。RD SYS-002/004、UI243/253、SS342/343 §6、既存018/078～081の固定ID/保持inode/strict形式と対応。5件ずつの取得・途中失敗時の所有材料消去に限定し、実systemd配布・DB/MQ接続は対象外。

fixtureはLinux/JDK25.0.4/Maven wrapper上の実一時file/保持channelと明示的な合成UID/ACL metadata。入力はWeb/API固定ID各5の`pt-public-<ID> LF`または `NKKEY1 LF v LF`＋32 zero byteのcanonical Base64＋LFで、秘密実体は使用しない。expectedはSS342の5+5 literal ID、SS343のbyte形式、Test内固定文字/zero配列から独立算出し、Production load/decode結果を期待値生成に用いない。

| Test ID | 入力・操作/目的 | 独立期待値・正常/境界/異常/例外/null/並行/再送 |
| --- | --- | --- |
| PT-OPS-CREDSET-001 | 両serviceで各5実fileを読む。password/key copyとversionを検査してzero、set close二回 | 各固定IDの期待材料のみ取得、5 open/5 close、reader一時buffer全zero。close冪等、出力redacted |
| PT-OPS-CREDSET-002 | null reader/service/ID、別service ID、kind違い、close済み利用 | null境界はNPE、外部ID/kindは非秘密固定拒否、close後コピー不可。DB/MQ key取り違えなし |
| PT-OPS-CREDSET-003 | 最後のfile欠落/形式不正、4件取得後にRuntime/Error注入 | 失敗を成功化せず同一例外を保持、取得済材料をcloseし、一時bufferを全zero。部分Setを返さない |
| PT-OPS-CREDSET-004 | 8 workerで32独立load/copy/close | copy毎に固定32 zero byte、全task成功、操作buffer全zero、shared state混入なし |
| PT-OPS-CREDSET-005 | callerがSetの公開monitorを保持したまま別threadでcopyPassword/close | private lockにより5秒内にcopy/close成功、外部monitorで秘密消去を妨害できない。BUG-259/YKT-194の再発防止 |

NPEを正常扱いでcatchしない。再送自体はこの起動時material所有部品の対象外で、外部再接続時の再取得は後続起動PTで確認する。Production全分岐・例外境界とJava6全coverage100%、静的解析0、負canary103、全53scope/hashを正式runで確認する。command `sh tools/quality/030_run_pgpt_verify.sh <新run ID>`、収集/保存照合 `python3 -B tools/quality/018_collect_verified_evidence_set.py <run ID>` と `--validate-only`。対象commit、実行日時、終了code、input/expected/actual、coverage、BUG/SSC、sanitized evidence path/hashは085結果と同Program manifestへ記録する。failed/flaky/skipped/not-runを合格に算入しない。
