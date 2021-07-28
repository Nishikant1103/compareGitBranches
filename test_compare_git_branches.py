import pytest
from compare_git_branches import GithubAuthorizor
from github import Github


@pytest.fixture(scope='module')
def github_automator():
    print("Setting up the test")
    github_access_token = Github()
    yield github_access_token
    print("Tearing down the test")


@pytest.mark.parametrize("access_token, github_username", [(None, 'pallets'), ('wrongtoken', 'Nishikant1103')])
def test_get_github_user(access_token, github_username):
    authorize = GithubAuthorizor(access_token)
    token, user, auth_status = authorize.get_github_user(github_username)
    assert token and user is not None
    assert type(auth_status) == bool


@pytest.mark.parametrize("access_token", [None, 'wrongtoken'])
def test_get_authorization_token(access_token):
    authorize = GithubAuthorizor(access_token)
    token, auth_status = authorize.get_authorization_token()
    assert token is not None
    assert type(auth_status) == bool
