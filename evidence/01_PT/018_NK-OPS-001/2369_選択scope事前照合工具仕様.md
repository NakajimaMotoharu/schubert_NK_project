# 選択scope事前照合工具仕様

2026-10-28 / F03 / BUG1993-YKT1741・BUG1994-YKT1742の再発防止。直前save0bcd337960b46dd8c69928ba3246d79531931d51はremote同一を確認。製品source e353b1f49a740a426031fdc199f7ce8b26081971は不変更。原計画・既実費・正式1964/53、17/190、工数nullを保持。

着手前見積り低0.5/標準2/高4週次共有枠pp、群上限10pp。主費WBS-F03のみ、工具再発防止費を製品完成へ算入しない。専有費・N/Tは測定できなければnull。元Writer群3/7/10や元eventは不変更。

PG12708は明示されたsource文字列・normal input hash・元registry row・既読Main一覧だけを純metadataで照合する。変更pathのcanonicalOwner/canonicalCostOwnerを実rowから保持し、packageや隣接classから推定しない。コメント/String/textblockを除いたNK直接importをnormal inputのJava外側型へ対応させ、既読一覧への欠落を報告する。wildcard、未解決、重複、未知owner、hash不一致、非正規pathは未解決又はエラーにする。自己作成した固定dictの独立期待値と非空の異常vectorを用いる。

読取対象は明示した公開manifestと既読57Main・二Testに限定。保留二工具、VM、DB、process、私有raw、鍵、原本、nativeへアクセスしない。新製品試験・Maven・Java実行は0。PG12708のcommandは `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg12708_fixture_scope_advisory.py`。実装後、静的Python lint、自己vector、当source原manifestとの照合を行い、独立PG12710で期待mappingとhash・出力を検証する。

本工具はadvisoryであって実行資格・HOLD解除・安全判定を発行しない。raw Java lexerはUnicode前処理、同package参照、継承、reflection、transitive call/initを証明せず、whole fixtureの実操作・副作用・所有・独立oracleは親が別途審査する。全coverage/451/F03合格へ変換しない。完了条件は固定vectorの正負検証、既読57＋二Testに欠落なし、故意のScenarioEntryRecord欠落と誤owner期待を検出、真正exit/hash・独立確認・記録保存。以後は別の許可済み通常PG/PTへ継続。
