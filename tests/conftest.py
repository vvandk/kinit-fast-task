# @Version        : 1.0
# @Create Time    : 2024/4/1 13:58
# @File           : conftest.py
# @IDE            : PyCharm
# @Desc           : 描述信息

import pytest


@pytest.fixture(scope="function")
def client():
    pass


@pytest.fixture(scope="function")
def resource_setup():
    yield


@pytest.fixture(scope="session")
def session_resource_setup():
    yield
