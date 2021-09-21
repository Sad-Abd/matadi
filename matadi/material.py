import numpy as np
import casadi as ca

from .apply import apply, modify as mdify


class Material:
    def __init__(self, x, fun, args=(), kwargs={}, compress=False):

        self.x = x
        self.fun = fun

        self.args = args
        self.kwargs = kwargs

        self._f = self.fun(self.x, *self.args, **self.kwargs)

        _h_diag = []

        self._h = []
        self._g = []

        # generate list of diagonal hessian entries and gradients
        for y in self.x:
            _hy, _gy = ca.hessian(self._f, y)
            _h_diag.append(_hy)
            self._g.append(_gy)

        # generate upper-triangle of hessian
        for i, g in enumerate(self._g):
            for j, y in enumerate(self.x):
                if j >= i:
                    if i != j:
                        self._h.append(ca.jacobian(g, y))
                    else:
                        self._h.append(_h_diag[i])

        # generate casADi function objects
        self._grad = ca.Function("g", self.x, self._g)
        self._hessian = ca.Function("h", self.x, self._h)

        # generate indices
        self._idx_gradient = [y.shape for y in x]
        self._idx_hessian = []

        if compress:
            for i in range(len(self._idx_gradient)):
                if np.all(np.array(self._idx_gradient[i]) == 1):
                    self._idx_gradient[i] = ()

        for i in range(len(self._idx_gradient)):
            a = self._idx_gradient[i]

            for j in range(len(self._idx_gradient)):
                b = self._idx_gradient[j]

                if j >= i:
                    self._idx_hessian.append((*a, *b))

    def grad(self, x, modify=None, eps=1e-5):
        "Return list of gradients."
        if modify is not None:
            y = [mdify(y, m, eps) for y, m in zip(x, modify)]
        else:
            y = x
        return apply(
            y, fun=self._grad, x_shape=self._idx_gradient, fun_shape=self._idx_gradient
        )

    def hessian(self, x, modify=None, eps=1e-5):
        "Return upper-triangle of hessian."
        if modify is not None:
            y = [mdify(y, m, eps) for y, m in zip(x, modify)]
        else:
            y = x
        return apply(
            y,
            fun=self._hessian,
            x_shape=self._idx_gradient,
            fun_shape=self._idx_hessian,
        )
