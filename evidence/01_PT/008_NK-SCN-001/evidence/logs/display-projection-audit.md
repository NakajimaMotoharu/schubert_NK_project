# BUG-035 / SSC-018 / YKT-031

現行正本の`program/app/src/main/java/dev/codex/schubert/repository/ScenarioRepository.java`は検索・明細とも`COALESCE(s.name,'') AS speaker`を表示する。`model/ScriptFileSummary.java#displayTitle`はchapter/sectionがNULLまたはJava isBlankの場合に次候補へ進み、最後はfile_nameを返す。NKの保持用speaker_labelは表示名の代替ではない。

旧PT-SCN-005のgoldenにあった`Alice label`は不適切なoracleであり、Current由来の`Alice`へ訂正する。修正理由は上位の現行互換契約で、production結果へexpectedを合わせるためではない。入力fixtureはnameとlabelを意図的に異ならせたまま維持し、誤投影を再検出できるようにする。

TitleはNULL/空/ASCII空白/Unicode空白と非blankの全境界、file一覧・明細・前後navigationを横断する。検索/一覧の是正だけでYKT-031を完了にせず、detail接続を追加試験する。旧362/363件成功記録は不足oracleを含む過去実行として保持し、最新再試験で置き換える。実master/本文/credentialは格納しない。

探索06でScenario17/FieldCodec5成功。Detail追加の0/200/201/10000/10001件、999voice、Current title/speaker、全閉鎖時の故障を確認。coverage探索でdetailの複数returnに由来するjavac TWRのnull-close guard 2分岐を確認した。JDBCの正常契約に反するnull ResultSetを作ってcoverageを増やさず、Optional結果を一か所で返す通常のcontrol flowへ整理する。除外設定・到達不能指定は追加しない。正式全体runはこの整理後に実行する。
