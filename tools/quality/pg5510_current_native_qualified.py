"""Current296/all1664 CRC+session join to genuine3896/562; no old exec or synthetic coverage."""
import ast
import json
import subprocess
import pg5072_current_native_qualified as previous
import pg5508_current_native_catalog as catalog
from pg5430_ownership_signed_candidate import validate_gate

SOURCE=catalog.role.SOURCE
W,P=previous.W,previous.P
FULL='pg5416-ownership-whole-qualified-v2'
SLOT='pg5510-current-native-qualified-v1'


def qualify(value):return validate_gate(value,SOURCE)


def qualify_snapshot():
    q=qualify(json.loads((W/FULL/'manifest.safe.json').read_bytes()))
    if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','diff',q['sourceSnapshot'],'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):
        raise ValueError('same clean qualified3896 source/Test/settings first')
    catalog.role.admission.authenticate_host()


def server():
    raw=previous.server()
    for old,new in(('PG5072','PG5510'),('PG4968','PG5414'),('qualified4968Tests','qualified5414Tests'),(previous.SOURCE,SOURCE)):
        raw=raw.replace(old,new)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in{3791,553,1650}:
                node.value={3791:3896,553:562,1650:1664}[node.value]
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def source():
    raw=previous.source()
    for old,new in((previous.catalog.SLOT,catalog.SLOT),(previous.SLOT,SLOT),(previous.FULL,FULL),('PG5072','PG5510')):
        raw=raw.replace(old,new)
    return raw


def main():
    template=previous.previous.previous
    ns={**template.transport.entry().__globals__,'CODE':server(),'SOURCE':SOURCE,'qualify_snapshot':qualify_snapshot}
    exec(compile(source(),'<current3896 exact native transport>','exec'),ns)
    with template.management_gate(P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':raise SystemExit(main())
