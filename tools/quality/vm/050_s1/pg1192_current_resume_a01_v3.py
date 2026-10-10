"""Fresh A01 after owned localhost SOCKS proof; preserve old failed attempts."""
import ast
import json
from pg1190_current_resume_a01_v2 import code as previous
from pg1041_cold_policy_diagnostic import W


def code():
    s = previous().replace('pg1190', 'pg1192').replace('PG1190', 'PG1192')
    marker='    os.umask(0o077)'
    if s.count(marker)!=1:raise ValueError('fixed transport admission insertion refused')
    s = s.replace(marker, "    from pg1191_chr_socks_owner import require_owner\n    require_owner()\n"+marker)
    s = s.replace("    before=json.loads(", "    require_owner()\n    before=json.loads(")
    s = s.replace("    after=json.loads(", "    require_owner()\n    after=json.loads(")
    ast.parse(s);return s


if __name__ == '__main__':
    env = {'__file__':__file__,'__name__':'actual_current_A01_v3'}
    exec(compile(code(),'<A01 owned SOCKS actual transport>','exec'),env);env['main']()
