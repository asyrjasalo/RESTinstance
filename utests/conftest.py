# -*- coding: utf-8 -*-


import pytest

from src import REST


@pytest.fixture()
def library():
    return REST
