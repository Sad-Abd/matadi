# matADi
Material Definition with Automatic Differentiation (AD)

[![PyPI version shields.io](https://img.shields.io/pypi/v/matadi.svg)](https://pypi.python.org/pypi/matadi/) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) ![Made with love in Graz (Austria)](https://img.shields.io/badge/Made%20with%20%E2%9D%A4%EF%B8%8F%20in-Graz%20(Austria)-0c674a) [![codecov](https://codecov.io/gh/adtzlr/matadi/branch/main/graph/badge.svg?token=2EY2U4ZL35)](https://codecov.io/gh/adtzlr/matadi) ![Codestyle black](https://img.shields.io/badge/code%20style-black-black) ![GitHub Repo stars](https://img.shields.io/github/stars/adtzlr/matadi?logo=github) ![PyPI - Downloads](https://img.shields.io/pypi/dm/matadi)

matADi is a simple Python module which acts as a wrapper on top of (casADi)[https://web.casadi.org/] for easy definitions of hyperelastic strain energy functions. Gradients (stresses) and hessians (elasticity tensors) are carried out by casADi's powerful and fast **Automatic Differentiation (AD)** capabilities. It is designed to handle inputs with trailing axes which is especially useful for the application in Python-based finite element modules.  Mixed-field formulations are supported as well.

## Installation
Install `matADi` from PyPI via pip.

```shell
pip install matadi
```

## Usage
First, we have to define a symbolic variable on which our strain energy function will be based on.

**Note**: *A variable of matADi is an instance of a symbolic variable of casADi (`casadi.SX.sym`). All `matadi.math` functions are simple links to (symbolic) casADi-functions.*

```python
from matadi import Variable, Material
from matadi.math import det, transpose, trace

F = Variable("F", 3, 3)
```

Next, take your favorite paper on hyperelasticity or be creative and define your own strain energy density function as a function of some variables `x` (where `x` is always a **list** of variables).

```python
def neohooke(x, mu=1.0, bulk=200.0):
    """Strain energy density function of a nearly-incompressible 
    Neo-Hookean isotropic hyperelastic material formulation."""

    F = x[0]
    
    J = det(F)
    C = transpose(F) @ F
    I1_iso = J ** (-2 / 3) * trace(C)

    return mu * (I1_iso - 3) + bulk * (J - 1) ** 2 / 2
```

With this simple Python function we create an instance of a Material, which allows extra `args` and `kwargs` to be passed to our strain energy function. This instance now enables the evaluation of both gradient (stress) and hessian (elasticity) via automatic differentiation, optionally also on input data with trailing axes.

```python
W = Material(
    x=[F],
    fun=neohooke,
    kwargs={"mu": 1.0, "bulk": 10.0},
)

# init some random deformation gradients
defgrad = np.random.rand(3, 3, 5, 100) - 0.5

for a in range(3):
    defgrad[a, a] += 1.0

P = W.gradient([defgrad])[0]
A = W.hessian([defgrad])[0]
```

## Hints
Please have a look at (casADi's documentation)[https://web.casadi.org/]. It is very powerful but unfortunately does not support all the Python stuff you would expect. For example Python's default if-statements can't be used in combination with a symbolic boolean operation. If you use `eigvals` to symbolically calculate eigenvalues and their corresponding gradients please call gradient and hessian methods with `W.gradient([defgrad], modify=True, eps=1e-5)` to avoid the gradient to be filled with NaN's. This is because the gradient of the implemented eigenvalue calculation is not defined for the case of repeated equal eigenvalues. The `modify` argument adds a small number `eps=1e-5` to the diagonal entries of the input data.