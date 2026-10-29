# 2528 ReleaseApproval値型 現whole8通常PT仕様

2026-10-29、PG-D829予定、source0061d178c/normal13832/全1843静的13838。開始0.5/2/4cap10、主F03/既担当費参照P01802・追加親予算0（現trace13846で開始前照合）、event2910のfresh値を保持。全145行Test/当Main全bodyを確認し、whole八を通常PT_DEFAULTとする。

NK-OPS001/SYS002004/OPS009/DAT009/UI212251253/SS343§11.1/SSC096/PG313、PT-OPS-APPROVAL001..008。対象は公開claimsの不変**値型**であり、署名検証・approval/permit発行・権限確認ではない。Test SHA1440d9326c5018f7d6a79ee50b1d9dd5bd61c0cf169d07a7ade1a1e82e5ef85b。入力は手書 `NKRELEASEAPPROVAL1`＋version1.2.3-PG313＋b64のASCII、MainはJDK Pattern/String/byte/Objectsだけ。File/Root/native/鍵/VM/DB/サービス/Graph9へ依存せず、自己pool4・barrier/Future各5秒だけ。fd/署名実体や原本へのアクセス0、既held wholeの一部抽出0。

|既Test ID末尾|入力/操作・独立期待|
|---|---|
|001|手書goldenをparseしてversion/digest固定literal、constructor→encodeも固定goldenへ比較。Production結果からexpected生成0。|
|002|version1～64文字/先頭制約、空/65/相対path/区切り/非ASCII/改行拒否。|
|003|null全境界・digest63/65/大文字/非hex/NUL拒否、非秘密b64固定。|
|004|MAX_BYTES192・入力0/192/193と非ASCII/BOM/未知key拒否。|
|005|CRLF/末尾LF不足/余剰/重複/未知key/順序逆/escape拒否。|
|006|入力/出力byte消去後もsnapshot独立・入力非破壊。|
|007|自己4taskをbarrierで同期し固定version文字列へ比較、共有状態なし。|
|008|header版/先頭空白/value空白拒否・version0/digest0×64の明示境界。|

異常/null/例外/byte境界/並行をwholeで維持、再送/実approval認証/署名/原本保持は別scope未受入。新ID/source変更0。旧173～178は歴史的cleanup契約の試験参照、当literal整理後wholeの実測へ転用0。

command=`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg13872_release_approval_whole_eight_pt.py`。JDK25.0.4/JUnit1.13.4/JaCoCo0.8.15、固定六jar/SDK/empty ENV、共有reporter単一Map8、13874で原XML/全source/Jar/一exec/session/CRC・完全ReleaseApproval一physicalの四counterを独立照合。miss保持、除外/reflection/旧exec union0。2529/専用manifestへcommand/環境/source/HEAD/実時刻/終了/期待actual/XML/counter/hashを保存。正式1964-53/17-190/工数null/QA051final/全HOLD・原予算受入を不変更、普通区切りで停止しない。
