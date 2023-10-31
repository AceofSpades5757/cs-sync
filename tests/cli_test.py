import unittest

from cs_sync.main import cli
from typer.testing import CliRunner


class TestStringMethods(unittest.TestCase):
    def setUp(self):
        # Typer's CLI Runner for Testing
        self.runner = CliRunner()

    def test_call(self):
        # Documented method of testing Typer applications.
        result = self.runner.invoke(cli, ["--help"])
        exit_code: int = result.exit_code
        self.assertEqual(0, exit_code)

        # Test that the CLI can be called
        # Unable to resolve using CI/CD tools at this time
        # process = subprocess.run(['cs-sync', '--help'], capture_output=True)
        # self.assertEqual(process.returncode, 0)


if __name__ == "__main__":
    unittest.main()
