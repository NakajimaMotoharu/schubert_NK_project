"""Bind completed same-source Receipt owned fault3, never actual acceptance/owner/DB proof."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17775-receipt-owned-graph-source-binding-v1'
RECORDS=[('PG17760-receipt-owned-graph-three-pt-v1','d8dd24ba736352e41dab8db845b6284af6cb6a59e45e0e8af42457745fafeae3'),('PG17762-receipt-owned-graph-three-post-v1','a2f6f4384ff5545642bbe0ab540e1d20e98292a810f6110c7229fa22055952c8'),('PG17764-receipt-owned-graph-three-independent-v1','dfc6bd5f5cb63c49128a9b1cc9d26401a43a4518bdaf44bf552567c542fa7a08'),('PG17770-current2810-receipt-owned-graph-registry-post-v1','5aa885a45dfdbf3ba89291ec70f85573935e641bb89d4a44e15a00d64920173f'),('PG17774-current2810-receipt-owned-graph-wbs-post-v1','888695ffb273f03bf25126afa446c3df0108a0a335987ccd4a0ccfc50bb2dd74')]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    rows=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=rows,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
