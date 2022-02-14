import subprocess
import unittest


class TestStringMethods(unittest.TestCase):
    def test_call(self):
        # Test that the CLI can be called
        process = subprocess.run(['cs-sync', '--help'], capture_output=True)
        self.assertEqual(process.returncode, 0)


if __name__ == '__main__':
    unittest.main()
