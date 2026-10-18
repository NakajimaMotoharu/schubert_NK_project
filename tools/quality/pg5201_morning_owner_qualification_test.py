import unittest
import pg5201_morning_owner_qualification as qualify
import pg5200_morning_owner_selected as entry


class InvocationJoin(unittest.TestCase):
    def test_explicit_three_only_and_other_case_retained(self):
        aliases=next(iter(entry.invocation_aliases().values()))
        self.assertEqual(len(aliases),3)
        observed=list(aliases)+['existing']
        self.assertEqual(qualify.normalized(observed,aliases),sorted(list(aliases.values())+['existing']))
        self.assertTrue(all(name.endswith('(Path)') for name in observed[:3]))

    def test_missing_alias_ambiguous_destination_or_collision_rejected(self):
        for methods,aliases in [(['one'],{'absent(Path)':'absent'}),
            (['one(Path)','two(Path)'],{'one(Path)':'same','two(Path)':'same'}),
            (['one','one(Path)'],{'one(Path)':'one'})]:
            with self.assertRaises(ValueError):qualify.normalized(methods,aliases)

    def test_unknown_signature_is_not_silently_stripped(self):
        self.assertEqual(qualify.normalized(['unknown(Path)'],{}),['unknown(Path)'])
        self.assertNotEqual(qualify.normalized(['unknown(Path)'],{}),['unknown'])


if __name__=='__main__':unittest.main()
