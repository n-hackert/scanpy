"""Like fixtures, but more flexible"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import pytest
from anndata.tests.helpers import asarray
from scipy import sparse

from .._helpers import (
    as_dense_dask_array,
    as_sparse_dask_array,
)
from .._pytest.marks import needs

if TYPE_CHECKING:
    from collections.abc import Iterable

    from _pytest.mark.structures import ParameterSet


def param_with(
    at: ParameterSet,
    *,
    marks: Iterable[pytest.Mark | pytest.MarkDecorator] = (),
    id: str | None = None,
) -> ParameterSet:
    return pytest.param(*at.values, marks=[*at.marks, *marks], id=id or at.id)


MAP_ARRAY_TYPES: dict[
    tuple[Literal["mem", "dask"], Literal["dense", "sparse", "sparse_chunks"]],
    tuple[ParameterSet, ...],
] = {
    ("mem", "dense"): (pytest.param(asarray, id="numpy_ndarray"),),
    ("mem", "sparse"): (
        pytest.param(sparse.csr_matrix, id="scipy_csr"),
        pytest.param(sparse.csc_matrix, id="scipy_csc"),
    ),
    ("dask", "dense"): (
        pytest.param(
            as_dense_dask_array,
            marks=[needs.dask, pytest.mark.anndata_dask_support],
            id="dask_array_dense",
        ),
    ),
    ("dask", "sparse"): (
        pytest.param(
            as_sparse_dask_array,
            marks=[needs.dask, pytest.mark.anndata_dask_support],
            id="dask_array_sparse",
        ),
        # probably not necessary to also do csc
    ),
}

ARRAY_TYPES_MEM = list(
    at for (strg, _), ats in MAP_ARRAY_TYPES.items() if strg == "mem" for at in ats
)
ARRAY_TYPES_DASK = list(
    at for (strg, _), ats in MAP_ARRAY_TYPES.items() if strg == "dask" for at in ats
)

ARRAY_TYPES_DENSE = list(
    at for (_, spsty), ats in MAP_ARRAY_TYPES.items() if spsty == "dense" for at in ats
)
ARRAY_TYPES_SPARSE = list(
    at for (_, spsty), ats in MAP_ARRAY_TYPES.items() if "sparse" in spsty for at in ats
)
ARRAY_TYPES_SPARSE_DASK_UNSUPPORTED = tuple(
    (
        param_with(at, marks=[pytest.mark.xfail(reason="sparse-in-dask not supported")])
        if attrs[0] == "dask" and "sparse" in attrs[1]
        else at
    )
    for attrs, ats in MAP_ARRAY_TYPES.items()
    for at in ats
)

ARRAY_TYPES = list(at for ats in MAP_ARRAY_TYPES.values() for at in ats)
