# NK-MED-001 相関ID期待値独立化結果

2026-10-26、dev-foundation、source 0867302e7c5eb95163213cb6340ac86f6898e137。Linux7.0.0-38-generic amd64、JDK25.0.4、Maven3.9.12、PMD7.28.0/Checkstyle14.3.0、GJF1.36.1。BUG1822/YKT1573・仕様005。Production source/Main21d不変、三Test sourceだけの相関ID引渡し是正。GJFによるStage SQL文字列分割はcompile-time同値で、token比較時のString結合正規化で照合した。初回の非正式比較が文字列をtoken列へ変換せずStage不一致を表示したため、実LEXでtoken化してから再比較し全三一致を確認した（製品試験の失敗/成功に算入しない）。

|記録|真正結果|manifest SHA-256|
|---|---|---|
|PG10368-media-correlation-static-v1|own session19991 exit1、PMD21/CS0/processing0。17duplicate、Test thread2/classloader2は適用性確認待ち。raw失敗保持、F03未受入|2716a22b7190801d5e39fce691a91415a64d4ea77a35381fdff1cb4bc0bdf994|
|PG10370-media-correlation-six-compile-v1|own session97389 exit0、正常六jar/PT0、固定snapshot/NullAway。旧成功の転用なし|83a5412fbceda6c07949301eef954a478b4a7b0ed7a53c453d8939dde39a4168|
|PG10372-media-correlation-post-v1|exit0、限定変換後全文token一致・元assertion保持、相関/decoder復帰metadata三変異拒否、全Main1843/他Test1940同byte・当三outer class変更|fc7ccf630a34447ef4cf81dd9036f585b74cf808a0cbe51124816bb30a6671c7|

manifestは018_NK-OPS-001/evidence/provisionalの各run内。commandは各同番号tools/quality/pg10368・10370・10372 Python工具、PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime。静的toolは旧b120 normal Main型を使用し、当worktree三source SHAを当normal086の入力と照合した。全元SUT/fixtureの実行なし。

REV001～003のsource/compile/metadata範囲は確認済み、REV004全静的は未達。製品PT=0/NOT_EXECUTED_HOLD、coverage未測定、全G03/F03/451未受入。正式1964PT/53scope、個別17/190、工数null、QA051 finalは不変更。静的17duplicateは次群で同値是正し、残四は実Test文脈へ分類する。保存push確認後にBUG1822のsource scopeだけ閉鎖可、実業務PTや所有安全を閉じない。
