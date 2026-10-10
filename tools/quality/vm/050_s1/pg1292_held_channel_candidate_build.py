"""New-only signed SSC261/769 candidate; installed D5/1068 and originals unchanged."""
import ast
from pg1068_stream_candidate_build import source as previous


def source():
    raw=previous()
    changes=[
      ('from pg1067_stream_candidate_contract','from pg1291_held_channel_candidate_contract'),
      ("SOURCE = 'd5b00104280028d9ea81b44c1d1c805f3c2861ed'","SOURCE = '769ddb15cd735c25fef581b5f9850ef9d0053c0f'"),
      ("OLD_SOURCE = '40ef6e894573d2ffab1d1732124960f9c98d5f97'","OLD_SOURCE = 'd5b00104280028d9ea81b44c1d1c805f3c2861ed'"),
      ("OLD = W / 'pg932-release-v1'","OLD = W / 'pg1068-release-v1'"),
      ("NEXT = W / 'pg1068-release-v1'","NEXT = W / 'pg1292-release-v1'"),
      ("SIG = P / 'pg1068-manifest-v1.sig'","SIG = P / 'pg1292-manifest-v1.sig'"),
      ('pg1018-stream-six-host-v2','pg1279-held-channel-six-host-v1'),
      ('c94cf95cddaef9fae4d3db02d3a732ee17a5ffdcc700714b14b4694fb077aab1','1c21767249100f4716fc9bebb8de86081dca92cf86e5ad9ac158ba457d259e7b'),
      ('b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524','0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d'),
      ("gate['tests'] == 3563","gate['tests'] == 3569"),
      ("and gate['newNativePending']","and not gate['global100']"),
      ('1632','1635'),
      ("b'0.1.0-PG932\\n'","b'0.1.0-PG1068\\n'"),
      ("b'0.1.0-PG1068\\n')","b'0.1.0-PG1292\\n')"),
      ("{'VERSION', 'api/api.jar'} <= changed","{'VERSION', *bootstrap_paths} <= changed"),
      ("data['release'] = '0.1.0-PG1068'","data['release'] = '0.1.0-PG1292'"),
      ("'pg1068-sign-v1.private.log'","'pg1292-sign-v1.private.log'"),
      ("'PG1068-candidate-build-v1'","'PG1292-candidate-build-v1'"),
      ("'pg1068-candidate-build-v1.safe.json'","'pg1292-candidate-build-v1.safe.json'"),
      ("'tests': 3560","'tests': 3569"),
      ("'changedClasses': 1","'changedClasses': 2"),
      ("'addedAbstractInterfaces': 0","'addedAbstractInterfaces': 2"),
      ("'addedInternalClasses': 0","'addedInternalClasses': 1"),
      ("'release': '0.1.0-PG1068'","'release': '0.1.0-PG1292'"),
    ]
    # Source/VERSION transitions use simultaneous replacements: never replace
    # the just-inserted prior name/bytes a second time.
    tokens={}
    for i,(old,new)in enumerate(changes):
        if old not in raw:raise ValueError('fixed qualified candidate substitution refused:'+str(i))
        token='__SSC261_BUILD_SUBSTITUTION_'+str(i)+'__'
        raw=raw.replace(old,token);tokens[token]=new
    for token,new in tokens.items():raw=raw.replace(token,new)
    ast.parse(raw);return raw


if __name__=='__main__':
    exec(compile(source(),'<same-source SSC261 signed candidate>','exec'),{'__file__':__file__,'__name__':'__main__'})
