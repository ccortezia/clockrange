# Third-Party Imports
from click.testing import CliRunner

# Local Imports
from clockrange.cli import clockrange_cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(clockrange_cli, ["--help"])
    assert result.exit_code == 0
    assert "HELP TEXT" in result.output


def test_cli_noargs():
    runner = CliRunner()
    result = runner.invoke(clockrange_cli, [])
    assert result.exit_code == 0
    assert result.output == ""
