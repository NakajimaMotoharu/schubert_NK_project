"""Independent normal owned-stop matrix, source-emission-only fixtures never stop permission."""
import inspect
import unittest
import pg4916_current_owned_test as reference
import pg5496_current_owned_sources as role
import pg5500_current_owned_dispatch as dispatch
import pg5502_current_owned_post as post


def matrix():
    raw=inspect.getsource(reference.Owned)
    for old,new in(('pg4916','pg5496'),('Pg4916','Pg5496'),('pg4918','pg5498'),
        ('pg4920','pg5500'),('pg4923','pg5501'),('04bbdb73b532537e3546191d72dee913b17629a0',role.SOURCE)):
        raw=raw.replace(old,new)
    old="role.composite.compose(original,{'before':{},'after':{},'context':{'fixtureOnly':True}},'b'*64)"
    if raw.count(old)!=1:raise ValueError('one pure-emission prefix argument fixture')
    raw=raw.replace(old,old[:-1]+",{'kind':'FAILED_HOST_CLOCK_BROWSER','fixtureOnly':True})",1)
    ns={**vars(reference),'__file__':__file__,'role':role,'dispatch':dispatch,'post':post}
    exec(compile(raw,'<new296 independent normal owned fixture matrix>','exec'),ns)
    return ns['Owned']


Owned=matrix()


class Transport(unittest.TestCase):
    def test_emitted_stage_all_current_identity_and_archive_paths(self):
        raw=dispatch.namespace()['stage']()
        for marker in('/opt/schubert-nk/releases/0.1.0-PG5430',role.SOURCE,role.BOM,dispatch.ARCHIVE,dispatch.REMOTE,dispatch.GUEST):self.assertIn(marker,raw)
        self.assertNotIn('/opt/schubert-nk/releases/0.1.0-PG4980',raw)


if __name__=='__main__':unittest.main()
