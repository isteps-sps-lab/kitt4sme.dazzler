from dazzler.dash.wiring import BasePath
import pytest
from typing import Optional


service_path_supply = ['', '/', '/s', '/s/', '/s/p', '/s/p/']


def mk_args(tenant_name: str, service_path: Optional[str] = None,
         board_path: Optional[str] = None) -> dict:
    args = {'tenant_name': tenant_name}
    if service_path is not None:
        args['service_path'] = service_path
    if board_path is not None:
        args['board_path'] = board_path

    return args


@pytest.mark.parametrize('init_args, want_path, want_tenant, want_sp, want_db',
[
    (mk_args('t'), '/dazzler/t/-/', 't', '/', '/'),

    (mk_args('t', ''), '/dazzler/t/-/', 't', '/', '/'),
    (mk_args('t', '/'), '/dazzler/t/-/', 't', '/', '/'),
    (mk_args('t', '/sp'), '/dazzler/t/sp/-/', 't', '/sp/', '/'),
    (mk_args('t', '/sp/'), '/dazzler/t/sp/-/', 't', '/sp/', '/'),
    (mk_args('t', 'sp/'), '/dazzler/t/sp/-/', 't', '/sp/', '/'),
    (mk_args('t', '/s/p'), '/dazzler/t/s/p/-/', 't', '/s/p/', '/'),
    (mk_args('t', 's/p'), '/dazzler/t/s/p/-/', 't', '/s/p/', '/'),
    (mk_args('t', '/s/p/'), '/dazzler/t/s/p/-/', 't', '/s/p/', '/'),
    (mk_args('t', 's/p/'), '/dazzler/t/s/p/-/', 't', '/s/p/', '/'),

    (mk_args('t', ''), '/dazzler/t/-/', 't', '/', '/'),
    (mk_args('t', '', ''), '/dazzler/t/-/', 't', '/', '/'),
    (mk_args('t', '', '/'), '/dazzler/t/-/', 't', '/', '/'),
    (mk_args('t', '', '/db'), '/dazzler/t/-/db/', 't', '/', '/db/'),
    (mk_args('t', '', 'db'), '/dazzler/t/-/db/', 't', '/', '/db/'),
    (mk_args('t', '', '/db/'), '/dazzler/t/-/db/', 't', '/', '/db/'),
    (mk_args('t', '', '/d/b'), '/dazzler/t/-/d/b/', 't', '/', '/d/b/'),
    (mk_args('t', '', '/d/b'), '/dazzler/t/-/d/b/', 't', '/', '/d/b/'),
    (mk_args('t', '', 'd/b/'), '/dazzler/t/-/d/b/', 't', '/', '/d/b/'),

    (mk_args('t', '/'), '/dazzler/t/-/', 't', '/', '/'),
    (mk_args('t', '/', ''), '/dazzler/t/-/', 't', '/', '/'),
    (mk_args('t', '/', '/'), '/dazzler/t/-/', 't', '/', '/'),
    (mk_args('t', '/', '/db'), '/dazzler/t/-/db/', 't', '/', '/db/'),
    (mk_args('t', '/', 'db'), '/dazzler/t/-/db/', 't', '/', '/db/'),
    (mk_args('t', '/', '/db/'), '/dazzler/t/-/db/', 't', '/', '/db/'),
    (mk_args('t', '/', '/d/b'), '/dazzler/t/-/d/b/', 't', '/', '/d/b/'),
    (mk_args('t', '/', '/d/b'), '/dazzler/t/-/d/b/', 't', '/', '/d/b/'),
    (mk_args('t', '/', 'd/b/'), '/dazzler/t/-/d/b/', 't', '/', '/d/b/'),

    (mk_args('t', '/sp'), '/dazzler/t/sp/-/', 't', '/sp/', '/'),
    (mk_args('t', '/sp', ''), '/dazzler/t/sp/-/', 't', '/sp/', '/'),
    (mk_args('t', '/sp', '/'), '/dazzler/t/sp/-/', 't', '/sp/', '/'),
    (mk_args('t', '/sp', '/db'), '/dazzler/t/sp/-/db/', 't', '/sp/', '/db/'),
    (mk_args('t', '/sp', 'db'), '/dazzler/t/sp/-/db/', 't', '/sp/', '/db/'),
    (mk_args('t', '/sp', '/db/'), '/dazzler/t/sp/-/db/', 't', '/sp/', '/db/'),
    (mk_args('t', '/sp', '/d/b'), '/dazzler/t/sp/-/d/b/', 't', '/sp/', '/d/b/'),
    (mk_args('t', '/sp', '/d/b'), '/dazzler/t/sp/-/d/b/', 't', '/sp/', '/d/b/'),
    (mk_args('t', '/sp', 'd/b/'), '/dazzler/t/sp/-/d/b/', 't', '/sp/', '/d/b/'),

    (mk_args('t', '/sp/'), '/dazzler/t/sp/-/', 't', '/sp/', '/'),
    (mk_args('t', '/sp/', ''), '/dazzler/t/sp/-/', 't', '/sp/', '/'),
    (mk_args('t', '/sp/', '/'), '/dazzler/t/sp/-/', 't', '/sp/', '/'),
    (mk_args('t', '/sp/', '/db'), '/dazzler/t/sp/-/db/', 't', '/sp/', '/db/'),
    (mk_args('t', '/sp/', 'db'), '/dazzler/t/sp/-/db/', 't', '/sp/', '/db/'),
    (mk_args('t', '/sp/', '/db/'), '/dazzler/t/sp/-/db/', 't', '/sp/', '/db/'),
    (mk_args('t', '/sp/', '/d/b'), '/dazzler/t/sp/-/d/b/', 't', '/sp/', '/d/b/'),
    (mk_args('t', '/sp/', '/d/b'), '/dazzler/t/sp/-/d/b/', 't', '/sp/', '/d/b/'),
    (mk_args('t', '/sp/', 'd/b/'), '/dazzler/t/sp/-/d/b/', 't', '/sp/', '/d/b/'),

    (mk_args('t', 'sp/'), '/dazzler/t/sp/-/', 't', '/sp/', '/'),
    (mk_args('t', 'sp/', ''), '/dazzler/t/sp/-/', 't', '/sp/', '/'),
    (mk_args('t', 'sp/', '/'), '/dazzler/t/sp/-/', 't', '/sp/', '/'),
    (mk_args('t', 'sp/', '/db'), '/dazzler/t/sp/-/db/', 't', '/sp/', '/db/'),
    (mk_args('t', 'sp/', 'db'), '/dazzler/t/sp/-/db/', 't', '/sp/', '/db/'),
    (mk_args('t', 'sp/', '/db/'), '/dazzler/t/sp/-/db/', 't', '/sp/', '/db/'),
    (mk_args('t', 'sp/', '/d/b'), '/dazzler/t/sp/-/d/b/', 't', '/sp/', '/d/b/'),
    (mk_args('t', 'sp/', '/d/b'), '/dazzler/t/sp/-/d/b/', 't', '/sp/', '/d/b/'),
    (mk_args('t', 'sp/', 'd/b/'), '/dazzler/t/sp/-/d/b/', 't', '/sp/', '/d/b/'),

    (mk_args('t', '/s/p'), '/dazzler/t/s/p/-/', 't', '/s/p/', '/'),
    (mk_args('t', '/s/p', ''), '/dazzler/t/s/p/-/', 't', '/s/p/', '/'),
    (mk_args('t', '/s/p', '/'), '/dazzler/t/s/p/-/', 't', '/s/p/', '/'),
    (mk_args('t', '/s/p', '/db'), '/dazzler/t/s/p/-/db/', 't', '/s/p/', '/db/'),
    (mk_args('t', '/s/p', 'db'), '/dazzler/t/s/p/-/db/', 't', '/s/p/', '/db/'),
    (mk_args('t', '/s/p', '/db/'), '/dazzler/t/s/p/-/db/', 't', '/s/p/', '/db/'),
    (mk_args('t', '/s/p', '/d/b'), '/dazzler/t/s/p/-/d/b/', 't', '/s/p/', '/d/b/'),
    (mk_args('t', '/s/p', '/d/b'), '/dazzler/t/s/p/-/d/b/', 't', '/s/p/', '/d/b/'),
    (mk_args('t', '/s/p', 'd/b/'), '/dazzler/t/s/p/-/d/b/', 't', '/s/p/', '/d/b/'),

    (mk_args('t', 's/p'), '/dazzler/t/s/p/-/', 't', '/s/p/', '/'),
    (mk_args('t', 's/p', ''), '/dazzler/t/s/p/-/', 't', '/s/p/', '/'),
    (mk_args('t', 's/p', '/'), '/dazzler/t/s/p/-/', 't', '/s/p/', '/'),
    (mk_args('t', 's/p', '/db'), '/dazzler/t/s/p/-/db/', 't', '/s/p/', '/db/'),
    (mk_args('t', 's/p', 'db'), '/dazzler/t/s/p/-/db/', 't', '/s/p/', '/db/'),
    (mk_args('t', 's/p', '/db/'), '/dazzler/t/s/p/-/db/', 't', '/s/p/', '/db/'),
    (mk_args('t', 's/p', '/d/b'), '/dazzler/t/s/p/-/d/b/', 't', '/s/p/', '/d/b/'),
    (mk_args('t', 's/p', '/d/b'), '/dazzler/t/s/p/-/d/b/', 't', '/s/p/', '/d/b/'),
    (mk_args('t', 's/p', 'd/b/'), '/dazzler/t/s/p/-/d/b/', 't', '/s/p/', '/d/b/'),

    (mk_args('t', '/s/p/'), '/dazzler/t/s/p/-/', 't', '/s/p/', '/'),
    (mk_args('t', '/s/p/', ''), '/dazzler/t/s/p/-/', 't', '/s/p/', '/'),
    (mk_args('t', '/s/p/', '/'), '/dazzler/t/s/p/-/', 't', '/s/p/', '/'),
    (mk_args('t', '/s/p/', '/db'), '/dazzler/t/s/p/-/db/', 't', '/s/p/', '/db/'),
    (mk_args('t', '/s/p/', 'db'), '/dazzler/t/s/p/-/db/', 't', '/s/p/', '/db/'),
    (mk_args('t', '/s/p/', '/db/'), '/dazzler/t/s/p/-/db/', 't', '/s/p/', '/db/'),
    (mk_args('t', '/s/p/', '/d/b'), '/dazzler/t/s/p/-/d/b/', 't', '/s/p/', '/d/b/'),
    (mk_args('t', '/s/p/', '/d/b'), '/dazzler/t/s/p/-/d/b/', 't', '/s/p/', '/d/b/'),
    (mk_args('t', '/s/p/', 'd/b/'), '/dazzler/t/s/p/-/d/b/', 't', '/s/p/', '/d/b/'),

    (mk_args('t', 's/p/'), '/dazzler/t/s/p/-/', 't', '/s/p/', '/'),
    (mk_args('t', 's/p/', ''), '/dazzler/t/s/p/-/', 't', '/s/p/', '/'),
    (mk_args('t', 's/p/', '/'), '/dazzler/t/s/p/-/', 't', '/s/p/', '/'),
    (mk_args('t', 's/p/', '/db'), '/dazzler/t/s/p/-/db/', 't', '/s/p/', '/db/'),
    (mk_args('t', 's/p/', 'db'), '/dazzler/t/s/p/-/db/', 't', '/s/p/', '/db/'),
    (mk_args('t', 's/p/', '/db/'), '/dazzler/t/s/p/-/db/', 't', '/s/p/', '/db/'),
    (mk_args('t', 's/p/', '/d/b'), '/dazzler/t/s/p/-/d/b/', 't', '/s/p/', '/d/b/'),
    (mk_args('t', 's/p/', '/d/b'), '/dazzler/t/s/p/-/d/b/', 't', '/s/p/', '/d/b/'),
    (mk_args('t', 's/p/', 'd/b/'), '/dazzler/t/s/p/-/d/b/', 't', '/s/p/', '/d/b/')
])
def test_combinations(init_args, want_path, want_tenant, want_sp, want_db):
    bp = BasePath(**init_args)

    assert str(bp) == want_path
    assert bp.tenant() == want_tenant
    assert bp.service_path() == want_sp
    assert bp.dashboard_path() == want_db


def test_init_error_on_invalid_tenant():
    with pytest.raises(AssertionError):
        BasePath(tenant_name='')


def test_str_repr_of_base_path_with_no_sp_ends_with_slash():
    bp = BasePath(tenant_name='t')
    got = str(bp)
    want = f"{BasePath.DAZZLER_ROOT}/t/-/"

    assert got == want


def test_tenant_of_base_path_with_no_sp():
    bp = BasePath(tenant_name='t')
    assert bp.tenant() == 't'


def test_sp_of_base_path_with_no_sp_is_slash():
    bp = BasePath(tenant_name='t')
    assert bp.service_path() == '/'


@pytest.mark.parametrize('sp', service_path_supply)
def test_str_repr_of_base_path_ends_with_slash(sp):
    bp = BasePath(tenant_name='t', service_path=sp)
    got = str(bp)

    if not sp.startswith('/'):
        sp = '/' + sp
    if not sp.endswith('/'):
        sp = sp + '/'
    want = f"{BasePath.DAZZLER_ROOT}/t{sp}-/"

    assert got == want


@pytest.mark.parametrize('sp', service_path_supply)
def test_tenant_of_base_path_with_sp(sp):
    bp = BasePath(tenant_name='t', service_path=sp)
    assert bp.tenant() == 't'


@pytest.mark.parametrize('sp', service_path_supply)
def test_sp_of_base_path_with_sp(sp):
    bp = BasePath(tenant_name='t', service_path=sp)
    if not sp.endswith('/'):
        sp = sp + '/'

    assert bp.service_path() == sp
