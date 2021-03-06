# -*- coding: utf-8 -*-
"""Unit tests for active_scanner."""
#
#    Copyright (C) 2020 Samsung Electronics. All Rights Reserved.
#       Author: Jakub Botwicz (Samsung R&D Poland)
#
#    This file is part of Cotopaxi.
#
#    Cotopaxi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    Cotopaxi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Cotopaxi.  If not, see <http://www.gnu.org/licenses/>.
#

import unittest

from cotopaxi.active_scanner import main
from cotopaxi.common_utils import get_local_ip
from cotopaxi.cotopaxi_tester import check_caps
from .common_test_utils import scrap_output, load_test_servers
from .common_runner import TimerTestRunner


class TestActiveScanner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            scrap_output(check_caps(), [])
        except SystemExit:
            exit(
                "This test suite requires admin permissions on network interfaces.\n"
                "On Linux and Unix run it with sudo, use root account (UID=0) "
                "or add CAP_NET_ADMIN, CAP_NET_RAW manually!\n"
                "On Windows run as Administrator."
            )

    def test_main_empty(self):
        output = scrap_output(main, [])
        self.assertTrue(
            "error: too few arguments" in output
            or "error: the following arguments are required" in output
        )

    def test_main_too_few_args(self):
        output = scrap_output(main, ["10"])
        self.assertTrue(
            "error: too few arguments" in output
            or "error: the following arguments are required" in output
        )

    def test_main_help(self):
        output = scrap_output(main, ["-h"])
        self.assertIn("positional arguments", output)
        self.assertIn("show this help message and exit", output)

    def test_main_no_ping(self):
        output = scrap_output(main, ["127.0.0.1", "10", "-V", "-T", "0.001"])
        self.assertIn("--ignore-ping-check", output)
        self.assertIn("skipping", output)

    def test_main_no_ping_ipv6(self):
        output = scrap_output(main, ["::1", "10", "-V", "-T", "0.001"])
        self.assertIn("--ignore-ping-check", output)
        self.assertIn("skipping", output)

    def test_active_scanner(self):
        local_ip = get_local_ip()
        print ("ip: {}".format(local_ip))

        config = load_test_servers()
        test_server_ip = config["COMMON"]["DEFAULT_IP"]
        dtls_servers = ["goldy"]
        for dtls_server in dtls_servers:
            port = config["DTLS_TEST_SERVERS"][dtls_server + "_port"]
            print ("test_server_ip: {} port: {}".format(test_server_ip, port))
            output = scrap_output(main, [test_server_ip, port, "-P", "DTLS"])
            self.assertIn("Finished active security scanning", output)
            self.assertIn("Starting scan: supported_protocol_versions", output)
            self.assertIn("Supported protocol versions", output)


if __name__ == "__main__":
    TEST_RUNNER = TimerTestRunner()
    unittest.main(testRunner=TEST_RUNNER)
