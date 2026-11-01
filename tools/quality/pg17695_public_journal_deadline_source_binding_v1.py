"""Completed public journal/deadline9 actual source binding; no native authority."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17695-public-journal-deadline-source-binding-v1'
RECORDS=[('PG17680-public-journal-deadline-nine-pt-v1','49473246237052e405cfbab6a41539fac97ffb6815b3bb6f9b1868191d55519c'),('PG17682-public-journal-deadline-nine-post-v1','1aa5ae001a9df7d4db9c140370c5f604b792b0e15d6e7f67359795a5d68707f1'),('PG17684-public-journal-deadline-nine-independent-v1','ee00c06d6e40e243ffe3b298d2b7725ac831d4021e4e95b4040be44b42d6f461'),('PG17690-current2793-journal-deadline-registry-post-v1','92d4dfdf98cbd115dbbbba439f820de1631d6442343d6aeea5c003fd92fdb83c'),('PG17694-current2793-journal-deadline-wbs-post-v1','d0725463e5c6bbb2258f3f8c118f2de025b972e11247dfa63bdb76f19fdd7d83')]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    rows=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=rows,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
