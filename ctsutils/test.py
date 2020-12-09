import numpy as np
import matplotlib.pyplot as plt

from ctsutils.cparameterspace import CParam, CParameterSpace


def foo(X, Y, Y2):
    """ """
    return (1 - X / 2 + X ** 5 + (Y + Y2) ** 3) * np.exp(-X ** 2 - (Y + Y2) ** 2)  # calcul du tableau des valeurs de Z



ps = CParameterSpace([CParam("x", np.linspace(-3, 3, 51)),
                      CParam("y", np.linspace(-2, 2, 41)),
                      CParam("y2", np.linspace(-1, 1, 31))])

# import pdb; pdb.set_trace()  # noqa BREAKPOINT
# x = ps.get_arr("x")

Z = ps.calc_function(foo, args_param_names=("x", "y", "y2"))

integrals = ps.calc_integral(Z, "x")

# fig, ax = plt.subplots(1, 1)
# ps.plot(Z, ordering_of_params_names=("y2", "y"), ax=ax)
# plt.show()

import pdb; pdb.set_trace()  # noqa BREAKPOINT

fig, ax = plt.subplots(1, 1)
ps.plot(integrals, z_label="integrals", ordering_of_params_names=("y2", "y"), ax=ax)

plt.show()
