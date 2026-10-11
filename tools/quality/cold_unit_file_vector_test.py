import unittest
from cold_unit_file_vector import matches


class UnitVectorTest(unittest.TestCase):
    def test_literal_complete_vector(self):
        self.assertTrue(matches([1,2,0,0,33184,1,48,100,101,'a'*64],
                                [1,2,0,0,33184,1,48,100,101],'a'*64))

    def test_negative_shapes_and_all_elements(self):
        metadata=[1,2,0,0,33184,1,48,100,101]
        expected=[1,2,0,0,33184,1,48,100,101,'a'*64]
        cases=[(None,metadata,'a'*64),('a'*64,metadata,'a'*64),
               (expected[:-1],metadata,'a'*64),(expected,None,'a'*64),
               (expected,metadata[:-1],'a'*64),(expected,metadata,None),
               (expected,metadata,'A'*64),(expected,metadata,'b'*64),
               ([True,*expected[1:]],metadata,'a'*64),
               (expected,[-1,*metadata[1:]],'a'*64)]
        for index in range(9):
            changed=metadata.copy();changed[index]+=1
            cases.append((expected,changed,'a'*64))
        for case in cases:
            with self.subTest(case=case):self.assertFalse(matches(*case))


if __name__=='__main__':unittest.main()
