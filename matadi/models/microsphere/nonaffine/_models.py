from ..._helpers import isochoric_volumetric_split
from ....math import sum1, diag, sqrt, cof
from ..quadrature._bazant_oh import BazantOh
from .._chain import langevin, linear


@isochoric_volumetric_split
def microsphere_nonaffine_stretch(C, p, f, kwargs, quadrature=BazantOh(n=21)):
    "Micro-sphere model: Non-affine stretch part."

    r = quadrature.points
    w = quadrature.weights

    nonaffine_stretch = sum1(sqrt(diag(r.T @ C @ r)) ** p * w) ** (1 / p)

    return f(nonaffine_stretch, **kwargs)


@isochoric_volumetric_split
def microsphere_nonaffine_tube(C, q, f, kwargs, quadrature=BazantOh(n=21)):
    "Micro-sphere model: Non-affine tube part."

    r = quadrature.points
    w = quadrature.weights

    Cs = cof(C)
    nonaffine_tubecontraction = sum1(sqrt(diag(r.T @ Cs @ r)) ** q * w)
    # nonaffine_areastretch = nonaffine_tube_contraction ** (1 / q)

    return f(nonaffine_tubecontraction, **kwargs)


@isochoric_volumetric_split
def microsphere_nonaffine_miehe_goektepe_lulei(C, mu, N, U, p, q):
    """Micro-sphere model: Combined non-affine stretch and
    tube model (for details see Miehe, Goektepe and Lulei (2004))."""

    kwargs_stretch = {"mu": mu, "N": N}
    kwargs_tube = {"mu": mu * N * U}

    quad = BazantOh(n=21)

    return microsphere_nonaffine_stretch(
        C, p=p, f=langevin, kwargs=kwargs_stretch, quadrature=quad
    ) + microsphere_nonaffine_tube(
        C, q=q, f=linear, kwargs=kwargs_tube, quadrature=quad
    )
