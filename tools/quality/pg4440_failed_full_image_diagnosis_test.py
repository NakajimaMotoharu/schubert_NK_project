"""Every full image/raw journal is persisted before comparison or classification."""
import unittest
import pg4440_failed_full_image_diagnosis as tool


class PreserveBeforeCompare(unittest.TestCase):
    def test_both_raw_and_full_images_are_saved_before_any_diagnosis(self):
        raw = tool.payload()
        first = raw.index("first_image_sha=save_private('canonical-first11.private.json'")
        second_read = raw.index('full_second,journal_second=canonical_image(snapshot())')
        second = raw.index("second_image_sha=save_private('canonical-second11.private.json'")
        diagnosis = raw.index('differences=[key for key in full_first')
        self.assertLess(first, second_read); self.assertLess(second_read, second); self.assertLess(second, diagnosis)
        self.assertLess(raw.index("second_journal_sha=save_private('journal-second-raw.private.json'"), diagnosis)
        self.assertIn('canonicalAdmissionAccepted=False', raw)
        self.assertIn("'allFieldsRetained':True", raw)
        self.assertIn('child.returncode==0', raw)


if __name__ == '__main__':
    unittest.main()
