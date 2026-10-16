"""Independent literal snapshot view tests; no VM/DB/start or Production calls."""
import copy
import unittest
import pg4250_current_admission_image as admission


def fixture():
    return {'units':{},'actors':{},'database':{'rows':{str(i):[]for i in range(24)},'peers':[],'locks':[]},'flocks':[],
            'durable':{'backup':{'synthetic':'unchanged'}},'native':{str(i)+'.exec':{'sha256':'a'*64}for i in range(52)},
            'startup':{},'runtime':{},'detailedActors':{},'configuration':{}}


class ViewTest(unittest.TestCase):
    def test_exact_projection_and_no_input_mutation(self):
        v=fixture();original=copy.deepcopy(v);pub={'unitFilesActual':{'synthetic-unit':[1,2]}}
        got=admission.project(v,pub)
        self.assertEqual(got,{'rows':{str(i):[]for i in range(24)},'durable':{'backup':{'synthetic':'unchanged'}},
            'oneTimeRuntime':{},'configuration':{},'unitFilesActual':{'synthetic-unit':[1,2]},'native':{str(i)+'.exec':{'sha256':'a'*64}for i in range(52)}})
        self.assertEqual(v,original)

    def test_missing_extra_or_none_refused(self):
        for value in [None,{},dict(fixture(),invented=True)]:
            with self.subTest(value=type(value)):
                with self.assertRaises(ValueError):admission.project(value,{})

    def test_nonquiescent_and_incomplete_refused(self):
        for key in ['actors','detailedActors','flocks','peers','locks','rows','native']:
            v=fixture()
            if key in ['peers','locks']:v['database'][key]=[{'synthetic':True}]
            elif key=='rows':v['database']['rows'].pop('0')
            elif key=='native':v['native'].pop('0.exec')
            else:v[key]=['synthetic']
            with self.subTest(key=key):
                with self.assertRaises(ValueError):admission.project(v,{})


if __name__=='__main__':unittest.main()
