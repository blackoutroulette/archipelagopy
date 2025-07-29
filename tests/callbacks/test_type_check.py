import inspect
from typing import Coroutine, Callable

import pytest

from archipelago_py import Client, ClientCallbackInterface

def get_coroutine_callbacks() -> list[tuple[str, Coroutine]]:
    return [
        (name, func)
        for name, func in inspect.getmembers(ClientCallbackInterface, inspect.iscoroutinefunction)
        if name.startswith("on_")
    ]

def get_non_coroutine_callbacks() -> list[tuple[str, callable]]:
    return [
        (name, func)
        for name, func in inspect.getmembers(ClientCallbackInterface, inspect.isfunction)
        if not inspect.iscoroutinefunction(func) and name.startswith("on_")
    ]

def id_func(t: tuple[str, Callable]) -> str:
    return t[0]

@pytest.mark.parametrize("coroutine", get_coroutine_callbacks(), ids=id_func)
def test_coroutine_patching(coroutine: tuple[str, Coroutine]):

    client = Client(0)
    name, _ = coroutine

    def non_coroutine():
        pass

    async def coroutine():
        pass

    with pytest.raises(TypeError):
        setattr(client, name, non_coroutine)

    # test no error is raised
    setattr(client, name, coroutine)

@pytest.mark.parametrize("func", get_non_coroutine_callbacks(), ids=id_func)
def test_non_coroutine_patching(func: tuple[str, Coroutine]):

    client = Client(0)
    name, _ = func

    def non_coroutine():
        pass

    async def coroutine():
        pass

    with pytest.raises(TypeError):
        setattr(client, name, coroutine)

    # test no error is raised
    setattr(client, name, non_coroutine)