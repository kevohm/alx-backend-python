#!/usr/bin/env python3
"""test_client
"""
import unittest
from client import GithubOrgClient
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, PropertyMock
from typing import Dict, Callable, Any
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """class hols tests for client.py
    """
    @parameterized.expand([("google"), ("abc")])
    def test_org(self, org: str) -> None:
        """test org method in GithubOrgClient
        """
        with patch("client.get_json", return_value={}) as json:
            obj = GithubOrgClient(org)
            self.assertEqual(obj.org, json.return_value)
            json.assert_called_once()

    def test_public_repos_url(self) -> None:
        """mock a property
        """
        with patch.object(GithubOrgClient, "org",
                          new_callable=PropertyMock) as org:
            org.return_value = {
                    "repos_url": "org"
                    }
            obj = GithubOrgClient("Google")
            self.assertEqual(obj._public_repos_url, "org")

    @patch("client.get_json", return_value=[])
    def test_public_repos(self, get):
        """test GithubOrgClient.public_repos
        """
        with patch.object(GithubOrgClient, "_public_repos_url",
                          new_callable=PropertyMock,
                          return_value="org") as m:
            obj = GithubOrgClient("org")
            self.assertEqual(obj.public_repos(), get.return_value)
            m.assert_called_once()
            get.assert_called_once()

    @parameterized.expand([({"key": "my_license"}, "my_license", False),
                          ({"key": "other_license"}, "my_license", False)])
    def test_has_license(self, data: Dict, value: str, expected: Any) -> None:
        """test for GithubOrgClient.has_license
        """
        self.assertEqual(GithubOrgClient.has_license(data, value), expected)


def get_repo(*args, **kwargs):
    """return repo data
    """
    class Resp:
        """return data
        """
        def __init__(self, data):
            """initialize object
            """
            self.data = data

        def json(self):
            """get data
            """
            return self.data
    if args[0] == "https://api.github.com/orgs/google":
        return Resp(TEST_PAYLOAD[0][0])
    if args[0] == TEST_PAYLOAD[0][0]["repos_url"]:
        return Resp(TEST_PAYLOAD[0][1])


@parameterized_class(
        ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
        [(TEST_PAYLOAD[0][0], TEST_PAYLOAD[0][1], TEST_PAYLOAD[0][2],
          TEST_PAYLOAD[0][3])]
        )
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """test the GithubOrgClient.public_repos method in an integration test
    """
    @classmethod
    def setUpClass(cls):
        """setup class
        """
        cls.get_patcher = patch("utils.requests.get", side_effect=get_repo)
        cls.get_patcher.start()
        cls.client = GithubOrgClient('google')

    @classmethod
    def tearDownClass(cls):
        """Destroy class
        """
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos method without license
        """
        self.assertEqual(self.client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos method with license
        """
        self.assertEqual(
            self.client.public_repos(license="apache-2.0"),
            self.apache2_repos)


if __name__ == "__main__":
    unittest.main()
