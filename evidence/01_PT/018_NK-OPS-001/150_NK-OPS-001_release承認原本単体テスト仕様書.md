# PG313 fixed release approval原本PT（着手前）

Program NK-OPS-001、予定ReleaseApproval codec/RootReleaseApprovalReader・fullBOM入口。RD SYS002/004/OPS009/DAT009、UI212/251/253、SS343§11.1/SSC095096・471D02/04/05。実装class/methodが確定したら431へ追跡し、各8件prefixをcollector/独立canaryへ登録する。未実装/未実行を合格扱いしない。

Approval codec独立goldenは `NKRELEASEAPPROVAL1\nversion=1.2.3-PG313\nmanifest_sha256=`＋64 literal lowercase b＋LF、Production encodeからexpectedを作らない。001literal encode/decode、002release1/64文字境界、003全field空/null/異常、004byte0/192/193・非ASCII、005固定順/LF/unknown/duplicate/trailing、006mutation/防御copy、007同時独立parse、008固定version/非canonical拒否を検証する。

Reader001真正固定root原本正常・全ownerclose、002固定名/任意pathfallback無し/null、003directory/file属性rootUIDGID/mode/link/dev/ino/ACL全境界、004全IO event/取得済全close/known-unknown同一例外複合、005読取0/short/overflow/EOF/位置/サイズ変化、006前後inode/namespace/current原本置換拒否、007割込/非root/同時独立owner、008actualnativehost-view/root固定Unit positiveを対象とする。borrowed host/context/M/Aを閉じず、保持FD/pathを外へ返さない。非root hostでのfactory拒否をactualroot positiveへ読み替えない。

署名・BOM受入は別接続specへ追加し、独立固定公開vector/署名誤り/別鍵/改変/原本発行順・全artifact固定path/size/SHA・未知file/dir・symlink・samejar・SQL CRC/同梱一致・承認digest/version/前後namespace/全closeのnegativeを持つ。署名原本発行が未実装ならfullgate false。line/method/class/branch100%/null静的/全例外・境界・並行、coverage安易除外禁止。実行command/sourcehash/XML/coverage/実VMhash/BUGは151以降へ保存予定。
