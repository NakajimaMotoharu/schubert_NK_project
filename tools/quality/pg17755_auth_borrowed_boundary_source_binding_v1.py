"""Bind actual borrowed authentication fault3 source/proof with constructor effects disclosed."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17755-auth-borrowed-boundary-source-binding-v1'
RECORDS=[('PG17740-auth-borrowed-boundary-three-pt-v1','827e6ab1aeeb00140d978867cebad6b97fe9f1240426de9aa699c769f4cc238c'),('PG17742-auth-borrowed-boundary-three-post-v1','f1082ea1d6aa3d8aad341dd00a03dde5f61b8bb1562bce759ab1304576af22bf'),('PG17744-auth-borrowed-boundary-three-independent-v1','0a4527c4c62b330601d228d8855befe9414bae0d9edaaededb4f29b706831316'),('PG17750-current2807-auth-borrowed-boundary-registry-post-v1','215189212c576794299460d92d4d5b3d33a3621a42e8aa93e89e06abe7ab16ba'),('PG17754-current2807-auth-borrowed-boundary-wbs-post-v1','a087cc050376d8c82ead49d2c0d3d1592c9f8c28594563fba68f5e76129c675c')]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    rows=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=rows,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
