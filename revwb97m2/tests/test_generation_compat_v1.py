import pytest
from revwb97m2.scripts.generation_compat_v1 import compare_dependencies


def test_exact_addition_accepted():
    compare_dependencies({'old':'a'},{'old':'a','adapter':'b'},{'adapter':'b'})


@pytest.mark.parametrize('current',[
    {'old':'changed','adapter':'b'}, {'adapter':'b'},
    {'old':'a','adapter':'changed'}, {'old':'a'},
    {'old':'a','adapter':'b','unknown':'c'},
])
def test_changed_missing_or_unknown_dependency_rejected(current):
    with pytest.raises(ValueError):compare_dependencies({'old':'a'},current,{'adapter':'b'})


def test_no_historical_override():
    with pytest.raises(ValueError):compare_dependencies({'old':'a'},{'old':'b'},{'old':'b'})
