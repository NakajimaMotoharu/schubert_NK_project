# SSC-461 Batch二JDBC境界の通常PT

BUG-3233／YKT-2680、WBS-F02／P004-05、UI241/251、SS311/332/333/341、SSC439の旧whole21を固定。MorningSqlFailuresTest12、JdbcResourceFailuresTest8、StorageReasonValueContractTest1。両Mainの差は既3箇所の呼出先を同じSQL APIのBootstrap所有へ移した点のみ。元試験本文、独立SQL型／fixed message／primary identity／cause・抑制・次例外の順位と有限性、storage Reason名義は同一blob。

今回一般化したStorage探索とBootstrapのadapterを実型で接続する。実DB・実batch起動・権限・Root・サービスは別対応。独立XML、当Core、byte・CRCと生counterを保存し、旧runの混用はしない。Storage旧1引数の物理違反を解除しない。
