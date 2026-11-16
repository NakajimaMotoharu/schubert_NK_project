# Checkpoint CLOSING独立追補

BUG3144/YKT2613、元A2-28.01 3.9/cap8内。NCHECK-CLOSING-004を新Testの第四定義に追加し、元12＋fatal3＋closing1＝16を一Unit/一execで実行する。新sourceが必要な普通capture分岐を補い、旧成功の確認再演やexec合算をしない。製品Main変更0。

公開Point.valueOfはBEFORE_EXEC/TERMINAL/CLOSINGを各固定enumと同一、UNKNOWNはIAE。API ordinary profileのCLOSINGはIAE/exports0。固定INSPECTOR ordinaryのterminal前CLOSINGは固定IOで試行消費、後のTERMINALは一度採取できるがCLOSING再試行はIOで追加export0。別ownerでTERMINAL→CLOSINGは固定invocation.terminal.exec/.closing.execの順に各一回、独立7byte GOLDEN、CLOSING再送はIO/追加export0。profileは固定literalを純parseするだけ、Fake Agentは固定vendor version/session/bytes、実agent起動/NativeFile/Root/権限/stop/VM/鍵等を呼ばない。正規/初期拒否/消費済拒否の各状態を別instanceで確認する。

原15の成功/9L4M7B未達を保持、enum compiler/実native残を推定でPASSにしない。全16の実XML/rawを再照合してから限定判断する。
