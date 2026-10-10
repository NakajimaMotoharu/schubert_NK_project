# cold所有SQL原因・独立再試験（PG1040～1048）

Program NK-OPS-001 / helper Pg1037ColdOwnedPreparation・owned_peer_sql、SS343/353 SSC243244、QA047、BUG1017/YKT786。Productionは40ef/PG932のまま。PG1039 prepareの失敗・UNKNOWN保持は未受入、正式24/1964/53は不変更。工具sourceは本証跡保存commitに含まれるblob、実診断は未commit工具のscript/class SHAを各manifestで束縛する。保存commit以外のsource成功に流用しない。

## 独立期待値・試験

| Test ID | 入力・操作 | 独立期待値 | 実結果 |
|---|---|---|---|
| PT-DEP-1041001 | six-root actual policy private/host | Root0・0755/0700・durable ext4rw・ACL0・同identity | actual0、0.810500s |
| PT-DEP-1043001 | readonly SPI/Writer/UUID拒否、完成原本二読 | cutoff23:31:22.087768Z、SUCCESS/end23:56:48.112404Z固定literal、namespace/normalclose | actual0、1.260219s、224read/12names |
| PT-DEP-1044001 | readonly local SPI、同原本 | 1043001と同じ固定literal | actual0/1.042003s、producer誤labelにより技術診断のみ・trace受入0 |
| PT-DEP-1045001 | 私有heap解析、全message redaction | arbitrary/raw情報非表示、例外class/BCIだけ | wrapper execute BCI78、SDK IOException再包装位置。原因文字列の復元なし |
| PT-DEP-1046001 | frozen child snapshotのみreadonly実行 | 失敗箇所のfunction/lineのみ、DB/Ref/Unit変更0 | actual1、snapshot142→command57→require53。旧失敗の正常化なし |
| PT-DEP-1047001 | backend5497、生成SQL | 手書きliteral peer条件、3 statement、advisory固定条件 | host PASS |
| PT-DEP-1047002 | backend0/2/5497/2147483646 | 数値後ANDは独立token、numeric trailing junk無し | host PASS |
| PT-DEP-1047003 | 旧counterexample`pid=5497and` | 独立regexで旧を拒否、新に非包含 | host PASS |
| PT-DEP-1048001 | 旧凍結SQLと修正生成SQLを実PGへ | 旧42601、新[他client0,他advisory0,同parent1]二読。expectedを生成SQLから計算しない | actual0、旧query actual1/42601、新query actual0二回 |

Fixtureは管理cold VM bootcbca/currentPG932/当Java5463-child5489、既成功原本とDBはreadonly観測。helperテストbackend境界0はDB close後の純token oracleであり生存peerを0へ変更しない。null/unknown契約は既1037三case/namespace契約を再実行、新SQL呼出元はauthenticated intの前提を保持。並行性は他client・別advisory ownerを合格へ含めない固定SQLであり、今回foreign peerを注入するfault試験は未実施。

Command：`python3 -B -m unittest discover -s tools/quality/vm/050_s1 -p pg1047_cold_owned_sql_test.py` 3/0、既1037同discover3/0。`python3 -B tools/quality/vm/050_s1/pg1048_cold_owned_sql_native.py` 0。OS/JDKは既toolchain/1038、実PG18.6・Python3.14.4、日付2026-10-10。

## 証跡・範囲

W=`/home/mini/codex/project1/work/pgpt-runs/PG379`。1048 `pg1048-cold-owned-sql-v1/manifest.safe.json`、07:47:22.575116～07:47:23.340078UTC、scriptSHA0764886cc1ab3a4c451cbc7fd19acb6b90bf0285380ebe08fa291042708a9811、logSHA1348e054b595f0369c28c4757a115414ca51c4fd674ad1a5bddda761583c22e8。1046 manifest actual1/logSHA89899cb2896a3c32177d3c499503dac5c1a48ec000dd949e62a8e30260057165、scriptSHA1f64ce183333e35db31ece006acb2187ebba33bb272d38214a2a9257257f4b61。

1041/1043/1044各W manifestを保持（1044実ディレクトリは`pg1044-cold-local-local-graph-diagnostic-v1`、run値PG1043-cold-local-graph-diagnostic-v1：非受入注記）。private heap/DB/credential/原本内容はGitへ格納0。heapは13,505,740byte/hash88dc79576abacd8ed435ee154171b286f35797d3997af733c2f3cbf25e071e51、host600。source/literal/messageを任意出力しない。

本試験はhelper原因別再試験・技術診断。Java Production coverage100の新認定ではない、native/whole受入/BUG1017完了0。元warm/cold peer SQL横展開の非該当根拠、DB-live+childの正規復旧契約/独立反例、旧actualexit、別fresh正常cold準備が残る。未commit試験結果を正式へ混ぜない。
