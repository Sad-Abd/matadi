import numpy as np

import matadi


def test_models():

    # data
    np.random.seed(2345537)
    FF = np.random.rand(3, 3, 5, 100)
    for a in range(3):
        FF[a, a] += 1

    pp = np.random.rand(5, 100)
    JJ = 1 + np.random.rand(5, 100) / 10

    models = [
        matadi.models.saint_venant_kirchhoff,
        matadi.models.neo_hooke,
        matadi.models.neo_hooke,
        matadi.models.mooney_rivlin,
        matadi.models.yeoh,
        matadi.models.third_order_deformation,
        matadi.models.ogden,
        matadi.models.arruda_boyce,
        matadi.models.extended_tube,
        matadi.models.van_der_waals,
    ]

    parameters = [
        {"mu": 1.0, "lmbda": 20.0},
        {"C10": 1.0},
        {"C10": 1.0, "bulk": 5000.0},
        {"C10": 1.0, "C01": 0.1, "bulk": 5000.0},
        {"C10": 1.0, "C20": 0.1, "C30": 0.01, "bulk": 5000.0},
        {"C10": 1.0, "C01": 0.1, "C11": 0.02, "C20": 0.1, "C30": 0.01, "bulk": 5000.0},
        {"mu": (1.0, 0.2), "alpha": (2.0, -1.5), "bulk": 5000.0},
        {"C1": 1.0, "limit": 3.2, "bulk": 5000.0},
        {"Gc": 0.1867, "Ge": 0.2169, "beta": 0.2, "delta": 0.09693, "bulk": 5000.0},
        {"mu": 1.0, "beta": 0.1, "a": 20, "limit": 5.0, "bulk": 5000.0},
    ]

    for model, kwargs in zip(models, parameters):

        HM = matadi.MaterialHyperelastic(model, **kwargs)
        HM_mixed = matadi.ThreeFieldVariation(HM)

        W = HM.function([FF])
        P = HM.gradient([FF])
        A = HM.hessian([FF])

        assert len(W) == 1
        assert len(P) == 1
        assert len(A) == 1

        W = HM_mixed.function([FF, pp, JJ])
        P = HM_mixed.gradient([FF, pp, JJ])
        A = HM_mixed.hessian([FF, pp, JJ])

        assert len(W) == 1
        assert len(P) == 3
        assert len(A) == 6


if __name__ == "__main__":
    test_models()
