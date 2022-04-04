from dazzler.dash.wiring import BasePath
import pytest


service_path_supply = ['', '/', '/s', '/s/', '/s/p', '/s/p/']


def test_init_error_on_invalid_tenant():
    with pytest.raises(AssertionError):
        BasePath(tenant_name='')


def test_str_repr_of_base_path_with_no_sp_ends_with_slash():
    bp = BasePath(tenant_name='t')
    got = str(bp)
    want = f"{BasePath.DAZZLER_ROOT}/t/"

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
    want = f"{BasePath.DAZZLER_ROOT}/t{sp}"

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
