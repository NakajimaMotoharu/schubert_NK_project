"""BUG981: new-only compiler; rebuilt four families never copy immutable outputs."""
from pathlib import Path
import ast
R=Path(__file__).resolve().parent
def regenerated(name):
    return any(name==base+'.class'or name.startswith(base+'$')and name.endswith('.class')for base in ('Pg797OwnedDatabase','Pg797OwnedDatabaseTest','Pg798DatabaseScope','Pg798DatabaseScopeTest'))
def profile_v2(raw):
    for stem in ('pg864-completed-tools','pg864-prepare-ro','pg864-verify','pg864-activate'):raw=raw.replace(stem+'-v1',stem+'-v2')
    return raw
def source():
    raw=(R/'pg864_compile.py').read_text().replace('-v1','-v2').replace('pg866-unused862-post-v2','pg866-unused862-post-v1').replace('pg832-release-v2','pg832-release-v1')
    raw=raw.replace("if name.endswith('.class'):","if name.endswith('.class') and not regenerated(name):")
    raw=raw.replace('raw=sources()','raw={name:profile_v2(value)for name,value in sources().items()}')
    ast.parse(raw);return raw
if __name__=='__main__':
    for family in ('Pg797OwnedDatabase','Pg797OwnedDatabaseTest','Pg798DatabaseScope','Pg798DatabaseScopeTest'):
        assert regenerated(family+'.class')and regenerated(family+'$Expected.class')and not regenerated(family+'Foreign.class')
    assert not regenerated('Pg387TrustedDeployment.class')and not regenerated('Pg797OwnedDatabase.java')
    exec(compile(source(),'<864 new-only regenerated compiler v2>','exec'),{'__file__':str(R/'pg864_compile_v2.py'),'__name__':'__main__','regenerated':regenerated,'profile_v2':profile_v2})
