"""
Validate the mac-keychain module
"""

import os

import pytest

from salt.exceptions import CommandExecutionError
from tests.support.case import ModuleCase
from tests.support.helpers import runs_on
from tests.support.runtests import RUNTIME_VARS


@pytest.mark.destructive_test
@runs_on(kernel="Darwin")
@pytest.mark.skip_if_not_root
class MacKeychainModuleTest(ModuleCase):
    """
    Integration tests for the mac_keychain module
    """

    @classmethod
    def setUpClass(cls):
        cls.cert = os.path.join(
            RUNTIME_VARS.FILES, "file", "base", "certs", "salttest.p12"
        )
        cls.cert_alias = "Salt Test"
        cls.passwd = "salttest"

    def tearDown(self):
        """
        Clean up after tests
        """
        # Remove the salttest cert, if left over.
        certs_list = self.run_function("keychain.list_certs")
        if self.cert_alias in certs_list:
            self.run_function("keychain.uninstall", [self.cert_alias])

    @pytest.mark.slow_test
    def test_mac_keychain_install(self):
        """
        Tests that attempts to install a certificate
        """
        install_cert = self.run_function("keychain.install", [self.cert, self.passwd])
        self.assertTrue(install_cert)

        # check to ensure the cert was installed
        certs_list = self.run_function("keychain.list_certs")
        self.assertIn(self.cert_alias, certs_list)

    @pytest.mark.slow_test
    def test_mac_keychain_uninstall(self):
        """
        Tests that attempts to uninstall a certificate
        """
        self.run_function("keychain.install", [self.cert, self.passwd])
        certs_list = self.run_function("keychain.list_certs")

        if self.cert_alias not in certs_list:
            self.run_function("keychain.uninstall", [self.cert_alias])
            self.skipTest("Failed to install keychain")

        # uninstall cert
        self.run_function("keychain.uninstall", [self.cert_alias])
        certs_list = self.run_function("keychain.list_certs")

        # check to ensure the cert was uninstalled
        try:
            self.assertNotIn(self.cert_alias, str(certs_list))
        except CommandExecutionError:
            self.run_function("keychain.uninstall", [self.cert_alias])

    @pytest.mark.slow_test
    def test_mac_keychain_get_friendly_name(self):
        """
        Test that attempts to get friendly name of a cert
        """
        self.run_function("keychain.install", [self.cert, self.passwd])
        certs_list = self.run_function("keychain.list_certs")
        if self.cert_alias not in certs_list:
            self.run_function("keychain.uninstall", [self.cert_alias])
            self.skipTest("Failed to install keychain")

        get_name = self.run_function(
            "keychain.get_friendly_name", [self.cert, self.passwd]
        )
        self.assertEqual(get_name, self.cert_alias)

    @pytest.mark.slow_test
    def test_mac_keychain_get_default_keychain(self):
        """
        Test that attempts to get the default keychain
        """
        salt_get_keychain = self.run_function("keychain.get_default_keychain")
        sys_get_keychain = self.run_function(
            "cmd.run", ["security default-keychain -d user"]
        )
        self.assertEqual(salt_get_keychain, sys_get_keychain)

    def test_mac_keychain_list_certs(self):
        """
        Test that attempts to list certs
        """
        cert_default = "com.apple.systemdefault"
        certs = self.run_function("keychain.list_certs")
        self.assertIn(cert_default, certs)
