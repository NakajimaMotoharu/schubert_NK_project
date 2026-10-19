"""Current0ea/all1664 physical CRC/session join to genuine3905/563; no old exec."""
import ast
import json
import subprocess
import pg5510_current_native_qualified as previous
import pg5680_current_native_catalog as catalog
from pg5598_current_signed_candidate import validate_gate
from pg5574_monitor_whole_qualification import SLOT as FULL

SOURCE=catalog.role.SOURCE
W,P=previous.W,previous.P
SLOT='pg5682-current-native-qualified-v1'


def qualify(value):return validate_gate(value,SOURCE)


def qualify_snapshot():
    q=qualify(json.loads((W/FULL/'manifest.safe.json').read_bytes()))
    if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','diff',q['sourceSnapshot'],'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):raise ValueError('same clean genuinely qualified3905 source/Test/config')
    catalog.role.admission.authenticate_host()


def server():
    raw=previous.server()
    for old,new in(('PG5510','PG5682'),('PG5414','PG5588'),('qualified5414Tests','qualified5588Tests'),(previous.SOURCE,SOURCE)):
        raw=raw.replace(old,new)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in{3896,562}:node.value={3896:3905,562:563}[node.value]
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def source():
    raw=previous.source()
    for old,new in((previous.catalog.SLOT,catalog.SLOT),(previous.SLOT,SLOT),(previous.FULL,FULL),('PG5510','PG5682')):raw=raw.replace(old,new)
    return raw


def main():
    template=previous.previous.previous.previous
    ns={**template.transport.entry().__globals__,'CODE':server(),'SOURCE':SOURCE,'qualify_snapshot':qualify_snapshot}
    exec(compile(source(),'<current3905 exact native transport>','exec'),ns)
    with template.management_gate(P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':raise SystemExit(main())
