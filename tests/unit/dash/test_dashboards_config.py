from typing import Any, List, Tuple

from dazzler.config import BoardAssembly, Settings
from dazzler.dash.wiring import DashboardsConfig



def builder_1() -> int:
    return 1


def builder_2() -> int:
    return 2


builder_1_pypath = 'tests.unit.dash.test_dashboards_config.builder_1'
builder_2_pypath = 'tests.unit.dash.test_dashboards_config.builder_2'


def assemble(builder: Any, tenant_name: str, service_path: str = '/',
             board_path: str = '/') -> Tuple[int, str, str, str]:
    return builder(), tenant_name, service_path, board_path


def call_assemble_with_config(cfg: Settings) \
        -> List[Tuple[int, str, str, str]]:
    target = DashboardsConfig(cfg)
    return [assemble(**d) for d in target.assemble_args()]


def test_empty_config():
    cfg = Settings(boards={})
    got = call_assemble_with_config(cfg)

    assert got == []


def test_one_tenant_with_no_board():
    cfg = Settings(boards={
        't': []
    })
    got = call_assemble_with_config(cfg)

    assert got == []


def test_one_tenant_with_one_board():
    cfg = Settings(boards={
        't': [
            BoardAssembly(builder=builder_1_pypath)
        ]
    })
    got = call_assemble_with_config(cfg)
    want = [assemble(builder_1, 't', '/', '/')]

    assert got == want


def test_one_tenant_with_many_boards():
    cfg = Settings(boards={
        't': [
            BoardAssembly(builder=builder_1_pypath),
            BoardAssembly(builder=builder_2_pypath, service_path='/sp',
                          board_path='/bp')
        ]
    })
    got = call_assemble_with_config(cfg)
    want = [
        assemble(builder_1, 't', '/', '/'),
        assemble(builder_2, 't', '/sp', '/bp')
    ]

    assert got == want


def test_many_tenants_where_some_have_no_boards():
    cfg = Settings(boards={
        't1': [
            BoardAssembly(builder=builder_1_pypath),
            BoardAssembly(builder=builder_2_pypath, service_path='/sp',
                          board_path='/bp')
        ],
        't2': []
    })
    got = call_assemble_with_config(cfg)
    want = [
        assemble(builder_1, 't1', '/', '/'),
        assemble(builder_2, 't1', '/sp', '/bp')
    ]

    assert got == want


def test_many_tenants_with_boards():
    cfg = Settings(boards={
        't1': [
            BoardAssembly(builder=builder_1_pypath, board_path='/b/p'),
        ],
        't2': [
            BoardAssembly(builder=builder_1_pypath),
            BoardAssembly(builder=builder_2_pypath, service_path='/sp',
                          board_path='/bp')
        ]
    })
    got = call_assemble_with_config(cfg)
    want = [
        assemble(builder_1, 't1', '/', '/b/p'),
        assemble(builder_1, 't2', '/', '/'),
        assemble(builder_2, 't2', '/sp', '/bp')
    ]

    assert got == want
