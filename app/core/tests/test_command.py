from unittest.mock import patch
from django.core.management import call_command
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTest(SimpleTestCase):
    def test_wait_for_db(self, patched_check):
        patched_check.return_value = True
        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])
