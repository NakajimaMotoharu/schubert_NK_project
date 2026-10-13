# Caddy公開inode内部境界（PG2112、未実行）

Program NK-OPS-001、CaddyPublicConfiguration/requireDirectoryMetadata・requireStableDirectory・requireInodeIdentity・requireNoAccessAcl。OPS009/UI251/SS342343/SSC178183、PG-D413、WBS-P018-03.02。独立oracleはroot/Caddy用既承認mode set、固定六identity、device>=0/inode>0、ACL非nullかつ空という値契約。Productionから期待値生成0。

PT-CADDY-2112-001：三mode/links2と9正常、owner/group/links1/別mode/regularfile/null拒否。002：六identity一項ずつdrift拒否、内容size/mtime/ctimeのみ変化正常、null二境界。003：device0/最大・inode1/最大正常、負/零境界拒否。004：空ACL正常、missing/nonempty拒否かつ元byte不変。Root/実UID/heldFDのauthorityをfixtureで作らず、純粋内部guardだけを検証。例外は固定IOException、nullはinvariantのNPEであり正常化catchなし。並行/再送・native Root/CA故障は本四testの対象外、既本体契約/後続nativeへ残す。

群0554凍結0.5/1.5/4共有pp。変更batchと既Caddy parser/metadata suiteを選択してformat/compile/null/static/PTを実行する。新Main byteの必要全回帰/native/全counter100/451/CHRは未実行、旧0fd成功を流用しない。未実行を合格に加算しない。実command/source/hash/count/coverage/終了codeは当限定manifestから追記する。秘密値・dump・rawsession/tokenはGit0。
