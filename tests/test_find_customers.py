# coding: utf-8


import pytest
import click.testing

from find_customers import cli


@pytest.fixture
def runner():
    return click.testing.CliRunner()


def test_file_is_required(runner):
    result = runner.invoke(cli)

    assert result.exit_code == 2
    assert 'Missing argument "file"' in result.output


def test_nothing_is_printed_for_empty_file(runner):
    result = runner.invoke(cli, ['-'], input='')

    assert result.exit_code == 0
    assert result.output == ''


def test_closest_customers_are_printed(runner):
    with runner.isolated_filesystem():
        with open('customers.txt', 'ab') as f:
            f.write(b'\n'.join((
                b'{"latitude": "0", "user_id": 7, "name": "John", "longitude": "0"}',
                b'{"latitude": "95", "user_id": 42, "name": "Peter", "longitude": "95"}'
            )))
        result = runner.invoke(cli, ['-c', '0', '0', 'customers.txt'])

    assert result.exit_code == 0
    assert result.output == 'John (7)\n'


def test_empty_lines_are_skipped(runner):
    with runner.isolated_filesystem():
        with open('customers.txt', 'ab') as f:
            f.write(
                b'\n'
            )
        result = runner.invoke(cli, ['customers.txt'])

    assert result.exit_code == 0
    assert result.output == ''


def test_invalid_line_is_warned(runner):
    with runner.isolated_filesystem():
        with open('customers.txt', 'ab') as f:
            f.write(
                b'Something that is not a json\n'
            )
        result = runner.invoke(cli, ['customers.txt'])

    assert result.exit_code == 1
    assert result.output == 'Failed to parse: "Something that is not a json"\n'


def test_not_all_fields_are_available(runner):
    with runner.isolated_filesystem():
        with open('customers.txt', 'ab') as f:
            f.write(
                b'{"name": "John"}\n'
            )
        result = runner.invoke(cli, ['customers.txt'])

    assert result.exit_code == 1
    assert result.output == 'Failed to parse: "{"name": "John"}"\n'


@pytest.mark.parametrize('line', [
    {"user_id": 42, "name": "John", "latitude": "fail"},
    {"user_id": 42, "name": "John", "latitude": "0", "longitude": "fail"},
])
def test_raises_if_lat_or_lon_is_not_a_number(runner, line):
    with runner.isolated_filesystem():
        with open('customers.txt', 'a') as f:
            f.write(
                '{0}\n'.format(line)
            )
        result = runner.invoke(cli, ['customers.txt'])

    assert result.exit_code == 1
    assert result.output == 'Failed to parse: "{0}"\n'.format(line)
