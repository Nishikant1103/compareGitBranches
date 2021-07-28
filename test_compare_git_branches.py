import pytest
from compare_git_branches import Authorize
from github import Github


@pytest.fixture(scope='module')
def g():
    print("Setting up the test")
    g = Github()
    yield g
    print("Tearing down the test")


@pytest.mark.parametrize("access_token, github_username", [(None, 'pallets'), ('wrongtoken', 'Nishikant1103')])
def test_get_github_user(access_token, github_username):
    authorize = Authorize(access_token)
    token, user, auth_status = authorize.get_github_user(github_username)
    assert token and user is not None
    assert type(auth_status) == bool


@pytest.mark.parametrize("access_token", [None, 'wrongtoken'])
def test_get_authorization_token(access_token):
    authorize = Authorize(access_token)
    token, auth_status = authorize.get_authorization_token()
    assert token is not None
    assert type(auth_status) == bool
