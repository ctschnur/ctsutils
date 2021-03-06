import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons

import operator

def find_nearest_idx(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def get_values_from_meshgrid(np_bool_array, mg=None, reduced_dimensions_indices=[], cps=None, return_with_names=True):
    """
    Args:
        reduced_dimensions_indices: a positive number by which the dimension of mg was reduced
                                    to arrive at the result from which np_bool_array comes (e.g. integration over one variable)
                                    reduces the dimension of the result by one (the index of that variable is then supplied to
                                    this argument) """


    if mg is None and cps is not None:
        mg = cps._meshgrid

    num_of_indep_var = len(mg)

    indexing_expr = [slice(None)] * num_of_indep_var
    for i in range(num_of_indep_var):
        if i in reduced_dimensions_indices:
            indexing_expr[i] = 0  # it could be any value, since the result does not depend on them (e.g. the calculated integral along x does not depend on a particular value of x)

    # import pdb; pdb.set_trace()  # noqa BREAKPOINT
    list_not_reduced = list((map(lambda n: (mg[n][tuple(indexing_expr)][np_bool_array]).item(), range(len(mg)))))
    reduction_tuple = tuple(filter(lambda i: i not in reduced_dimensions_indices, range(num_of_indep_var)))
    list_reduced = list(operator.itemgetter(*reduction_tuple)(list_not_reduced))

    if return_with_names == True:
        assert cps is not None
        list_of_param_names = [cp.name for cp in cps.cparams_list]
        reduced_list_of_param_names = list(operator.itemgetter(*reduction_tuple)(list_of_param_names))
        list_reduced_with_param_names = None
        return [list_reduced, tuple(zip(reduced_list_of_param_names, list_reduced))]  # return two things
    else:
        return list_reduced  # return one thing


def get_indices_from_np_where_query(np_where_query):
    """ """
    return tuple(map(lambda el: np.int(el), np.where(np_where_query)))


def shape_arrays_for_pcolor_plotting(ps, indexing_list_indep_vars, ordered_params, dep_var_mgf):
    """ """

    X = ps.get_mgf_arr(ordered_params[0].name)[
        tuple(indexing_list_indep_vars)]
    Y = ps.get_mgf_arr(ordered_params[1].name)[
        tuple(indexing_list_indep_vars)]
    Z = None

    if (np.shape(dep_var_mgf) == np.shape(X) and
        np.shape(dep_var_mgf) == np.shape(Y)):
        Z = dep_var_mgf
        # delivered in the appropriate shape to be plotted (e.g. after integrating out one dimension, i.e.
        # function with signature (N^d x N^d x ...) -> N^(d-1) evaluated and passed to this plotting function
        # in the right shape)
        print("plot: Z is already in the right shape")
    else:
        dep_var_mgf_dim = len(np.shape(dep_var_mgf))
        dim_reduction = ps.get_dimension() - dep_var_mgf_dim

        indexing_list_dep_var = indexing_list_indep_vars[dim_reduction:]
        # dimensionality reduced by an operation -> e.g. integration
        # -> cannot index the result with the original number of indices
        # index it from back to front until dep_var_mgf's dimensions run out
        # -> then you will get 2 dimensions for the pcolor plot

        Z = dep_var_mgf[tuple(indexing_list_dep_var)] # function with signature (N^d x N^d x ...) -> N^d evaluated

    return [X, Y, Z]

class CParam:
    def __init__(self, name, np_arr, unit=None):
        """
        Args:
            name: string
            np_arr: numpy array
            unit: set the unit as a string
        """
        self.name = name
        self.np_arr = np_arr
        self.unit = unit

    def get_unit_str(self):
        """ """
        if self.unit is None:
            return ""
        return self.unit

    def get_label_str(self):
        """ """
        if self.unit is not None:
            return self.name + " in " + self.get_unit_str()

        return self.name

class CSlider(Slider):
    # def __init__(self, param, *mpl_slider_args, **mpl_slider_kwargs):
    #     """
    #     Args:
    #         mpl_slider_args: (ax, label, valmin, valmax) """
    #     self.mpl_slider = Slider(*mpl_slider_args, **mpl_slider_kwargs)

    def on_changed(self, func_with_val_and_args, args_opt=()):
        """
        Allows to extend the function to have more than just val as it's argument
        """
        on_changed_func = lambda val, args=args_opt: func_with_val_and_args(val, *args) # this sets fixed references to the args
        # matplotlib.widgets can still call func(val) as before, just that I packed args into it

        Slider.on_changed(self, on_changed_func)

class CParameterSpace:
    def __init__(self, cparams_list):
        """ """
        self.cparams_list = cparams_list

        for cp in self.cparams_list:
            vars(self)[cp.name] = cp

        self._meshgrid = None
        self._make_meshgrid()

    def _make_meshgrid(self):
        """ once the cparams_list is initialized, use numpy's meshgrid to
        create multidimensional arrays of the same shape for each parameter.
        Always make sure that indexing is 'ij', otherwise the dimensions will
        switch around. """
        just_arrays = [cparam.np_arr for cparam in self.cparams_list]
        self._meshgrid = np.meshgrid(*just_arrays, indexing="ij")

    def get_mgf_arr(self, param_name):
        """ a meshgridified array is one of the return values of A, B, _ = np.meshgrid(a, b, ...);
        they all have the same dimensionality so that they can be plugged into a normal mathematical
        python function """
        if self._meshgrid is not None:
            return self._meshgrid[self.get_index_of(param_name)]
        else:
            print("no _meshgrid generated yet")
            exit(1)

    def get_index_of(self, name):
        """ """
        els = []
        for i, cp in enumerate(self.cparams_list):
            if cp.name == name:
                els.append(i)

        if len(els) == 1:
            return els[0]
        else:
            print("parameter occurs not once: ", els)
            exit(1)

    def get_param_by_name(self, name):
        """ """
        els = []
        for i, cp in enumerate(self.cparams_list):
            if cp.name == name:
                els.append(cp)

        if len(els) == 1:
            return els[0]
        else:
            print("parameter contained twice: ", els)
            exit(1)

    def get_arr(self, name):
        """ """
        els = []
        for cp in self.cparams_list:
            if cp.name == name:
                els.append(cp)

        if len(els) == 1:
            return els[0].np_arr
        else:
            print("parameter contained twice: ", els)
            exit(1)


    def get_dimension(self):
        """ """
        return len(self.cparams_list)

    def get_param_names(self):
        """ """
        return [cparam.name for cparam in self.cparams_list]

    def _make_sliders(self, indexing_list_indep_vars, ordered_params, ordering_of_params_name_and_value, dep_var_mgf, fig, ax):
        """ for all dimensions > 2, a slider is made """
        self.csliders = []

        if len(ordered_params) <= 2:
            print("no sliders generated, len(ordered_params) <= 2 ")
            return

        # continue here with plotting sliders for the parameters that are not visible in the color plot

        for i, param in enumerate(ordered_params[2:]):

            fig.subplots_adjust(left=0.25, bottom=0.05 + 0.05 * i + 0.2)
            mpl_slider_ax = plt.axes([0.1, 0.05 + 0.05 * i, 0.65, 0.03])

            index_expr = indexing_list_indep_vars[self.get_index_of(param.name)] # either an integer or a slice

            init_val = None
            mpl_slider_kwargs = {}

            if isinstance(index_expr, int) or isinstance(index_expr, np.int64):
                init_val = param.np_arr[int(index_expr)]
                mpl_slider_kwargs["valinit"] = init_val
            elif isinstance(index_expr, slice):
                if isinstance(index_expr.start, int):
                    init_val = param.np_arr[index_expr.start]
                    mpl_slider_kwargs["valinit"] = init_val
                else:
                    print("index_expr.start is not an int : ", index_expr)
            else:
                print("err: index_expr neither an int nor a slice : ", index_expr)
                exit(1)

            # slider = Slider(mpl_slider_ax, param.name, np.min(param.np_arr), np.max(param.np_arr), **mpl_slider_kwargs)

            cslider = CSlider(mpl_slider_ax, param.name, np.min(param.np_arr), np.max(param.np_arr), **mpl_slider_kwargs)

            cslider.on_changed(CParameterSpace.update_func, args_opt=(cslider, self, param, ordering_of_params_name_and_value, dep_var_mgf, fig, ax))

            self.csliders.append(cslider)

            # print("making slider of " + param.name + ", with init val: ", init_val)

    # TODO
    @staticmethod
    def update_func(val, cslider, cps, param, ordering_of_params_name_and_value, dep_var_mgf, fig, ax):
        """ """
        if not (param.np_arr == val).any(): # if val is not exactly on a data point
            nearest_idx = find_nearest_idx(param.np_arr, val)
            nearest_val = param.np_arr[nearest_idx]
            # print("resetting slider for ", param.name, " from ", val, " to ", nearest_val)
            cslider.set_val(nearest_val)

        # update the pcolor chart
        updated_ordering_of_params_name_and_value = []

        contains_it = False
        for i, (asked_pname, asked_pvalue) in enumerate(ordering_of_params_name_and_value):
            new_tuple = [asked_pname, asked_pvalue]
            if asked_pname == param.name:
                new_tuple[1] = val
                contains_it = True

            updated_ordering_of_params_name_and_value.append(tuple(new_tuple))

        if contains_it == False: # in case it's not contained yet, it must be added
            updated_ordering_of_params_name_and_value.append(
                (param.name, val))

        indexing_list_indep_vars, ordered_params = cps._get_indexing_list_and_ordered_params(updated_ordering_of_params_name_and_value)

        X, Y, Z = shape_arrays_for_pcolor_plotting(cps, indexing_list_indep_vars, ordered_params, dep_var_mgf)
        c = ax.pcolor(X, Y, Z# , shading="nearest"
        )
        # cbar = fig.colorbar(c, ax=ax)
        # cbar.ax.set_ylabel(z_label, rotation=-90, va="bottom")

        # update the slider to show the actual value of the grid point, not the continuous slider value
        index = indexing_list_indep_vars[cps.get_index_of(param.name)]
        assert isinstance(index, int) or isinstance(index, np.int64)
        grid_value = param.np_arr[index]

        fig.canvas.draw_idle()
        # print("updating slider of " + param.name + ", ", val, "updated_ordering_of_params_name_and_value: ", updated_ordering_of_params_name_and_value)

    def _get_indexing_list_and_ordered_params(self, ordering_of_params_name_and_value):
        """
        used in preparation for plotting with pcolor and sliders
        Args:
            ordering_of_params_name_and_value: list of tuples (param name, value); if no specific value put None for value
        Returns:
            indexing_list_indep_vars,  : a list that gets unpacked to be the indexing for the arrays provided by meshgrid
            ordered_params  :
            """

        # import pdb; pdb.set_trace()  # noqa BREAKPOINT
        # always supply what you want to have plotted
        assert len(ordering_of_params_name_and_value) >= 2

        asked_ordering_names = [param_name for param_name, value in ordering_of_params_name_and_value]
        asked_ordering_values = [value for param_name, value in ordering_of_params_name_and_value]

        # check if the param names are correct
        assert (False not in [param_name in self.get_param_names()
                              for param_name, value in ordering_of_params_name_and_value])

        ordered_param_names = []
        indexing_list_indep_vars = [None] * self.get_dimension()

        # the first two are always explicitly given
        for j, (asked_pname, asked_def_pvalue) in enumerate(ordering_of_params_name_and_value[:2]):
            ordered_param_names.append(asked_pname)
            indexing_list_indep_vars[self.get_index_of(asked_pname)] = slice(None)


        if len(ordering_of_params_name_and_value) > 2:
            for j, (asked_pname, asked_def_pvalue) in enumerate(ordering_of_params_name_and_value[2:]):
                ordered_param_names.append(asked_pname)

                # the following ones that are given have an initial value of interest
                if asked_def_pvalue is not None:
                    # get the closest calculated point to the asked default value

                    nearest_idx = find_nearest_idx(self.get_arr(asked_pname), asked_def_pvalue)
                    nearest_val = self.get_arr(asked_pname)[nearest_idx]
                    indexing_list_indep_vars[self.get_index_of(asked_pname)] = nearest_idx

                    # print("finding nearest value to", asked_pname, ": provided value : ", asked_def_pvalue,
                    #       ", nearest idx: ", nearest_idx, ", nearest value : ", nearest_val)
                else:
                    # no default value supplied -> just get the 0th index
                    indexing_list_indep_vars[self.get_index_of(asked_pname)] = 0

        # complete the ordering of not explicitly given params in second pass
        for cparam in self.cparams_list:
            if cparam.name not in ordered_param_names:
                ordered_param_names.append(cparam.name)
                indexing_list_indep_vars[self.get_index_of(cparam.name)] = 0

        ordered_params = [self.get_param_by_name(param_name) for param_name in ordered_param_names]

        return indexing_list_indep_vars, ordered_params



def plot(cps, dep_var_mgf, ordering_of_params_name_and_value=[],
         fig=None, ax=None, z_label=""):
    """
    Args:
        ordering_of_params_name_and_value: list of tuples (param name, default value)
                            the frist two independent parameters appear on x and y axes of the color plot
                            the others (if specified) appear as sliders in the specified order.
    """

    if ax is None:
        ax = plt.gca()

    if fig is None:
        fig = plt.gcf()

    if cps.get_dimension() == 1:
        ax.plot(dep_var_mgf[:],  # just one dimension, i.e. take all independent values of that dimension
                # if there is only one parameter, it must have index 0
                cps.get_arr(0),
                "k-")
    elif cps.get_dimension() >= 2.:
        # make color plot with cps.get_dimension() - 2 sliders below to vary the other parameters
        # this contains in the end an expression like [:, :, :, 2, :] (where ":" is equivalent to slice(None))

        indexing_list_indep_vars, ordered_params = cps._get_indexing_list_and_ordered_params(ordering_of_params_name_and_value)

        # if there are more than 2 dimensions (free parameters), plot sliders for the values of the other dimensions
        cps._make_sliders(indexing_list_indep_vars, ordered_params, ordering_of_params_name_and_value, dep_var_mgf, fig, ax)

        # plot X, Y, Z data, where X, Y, Z must have the same np.shape() tuple (2d tuple!)
        X, Y, Z = shape_arrays_for_pcolor_plotting(cps, indexing_list_indep_vars, ordered_params, dep_var_mgf)

        assert np.shape(X) == np.shape(Y) == np.shape(Z) and len(np.shape(X)) == 2
        c = ax.pcolor(X, Y, Z, # shading="auto"
        )
        cbar = fig.colorbar(c, ax=ax)
        cbar.ax.set_ylabel(z_label, rotation=-90, va="bottom")

        ax.set_xlabel(ordered_params[0].get_label_str())
        ax.set_ylabel(ordered_params[1].get_label_str())


def calc_integral(cps, dep_var_mgf,
                  param_to_integrate_over_name):
    """
    Args:
        dep_var_mgf: these are the actual y values
        param_to_integrate_over: name of param to integrate over -> x values
    """

    return np.trapz(dep_var_mgf,
                    x=cps.get_arr(param_to_integrate_over_name),
                    axis=cps.get_index_of(param_to_integrate_over_name))


def calc_function(cps, f, args_param_names=()):
    """ """
    if len(args_param_names) == 0:
        print("nothing sampled!")
        return None

    # check that all shapes are equal. only then they can be processed correctly by numpy
    shapes = np.array([np.shape(cps.get_mgf_arr(name)) for name in args_param_names])
    assert (shapes == shapes[0]).all()

    meshgridifed_arrays = [cps.get_mgf_arr(name) for name in args_param_names]
    return f(*meshgridifed_arrays)

def tuple_pull_to_front(orig_tuple, *tuple_keys_to_pull_to_front):
    """
    Args:
        orig_tuple: original tuple of type (('lS', 5.6), ('lT', 3.4000000000000004), ('ZT', 113.15789473684211), ('ZS', 32.10526315789474))
        *tuple_keys_to_pull_to_front: keys of those tuples that (in the given order) should be pulled to the front of the orig_tuple
    """
    orig_lst = list(orig_tuple)
    new_lst = []
    new_lst2 = []

    for otup in orig_lst:
        if otup[0] in tuple_keys_to_pull_to_front:
            new_lst.append(otup)
        else:
            new_lst2.append(otup)

    new_lst.extend(new_lst2)
    return new_lst

def get_twotuple_value(twotuple_tuple_or_list, key):
    """ from a tuple like (('lS', 5.6), ('lT', 3.4000000000000004)), get the value from giving a key """
    return list(filter(lambda el: el[0] == key, list(twotuple_tuple_or_list)))[0][1]

def linspace_around_value(middle_value, interval_around, howmany):
    """
    Args:
        interval_around: tuple of the form (*,*), or scalar, or (*, *, Bool: percentage)
    """
    start_mod = 0
    stop_mod = 0

    percentage_p = len(list(interval_around)) > 2 and interval_around[2] == True # this means percentage

    if isinstance(interval_around, tuple):
        start_mod = interval_around[0]
        stop_mod = interval_around[1]

        if percentage_p == True:
            start_mod *= middle_value * 1./100.
            stop_mod *= middle_value * 1./100.
    else:
        assert interval_around >= 0
        start_mod = -interval_around
        stop_mod = interval_around

        if percentage_p == True:
            start_mod *= middle_value * 1./100.
            stop_mod *= middle_value * 1./100.

    return np.linspace(middle_value + start_mod,
                       middle_value + stop_mod,
                       howmany)

from copy import deepcopy

def get_cparams_refined_ranges_around_minimum(cps, minimum_indep_vars_tuple, which_to_update_tuples_list):
    """
    Args:
        minimum_indep_vars_tuple: coarse minimum around which to generate new ranges
        *which_to_update_tuples: list of which to update
    """
    cparams_new = [deepcopy(el) for el in cps.cparams_list]
    for cp in cparams_new:
        for ut in which_to_update_tuples_list:
            if ut[0] == cp.name:
                # print(minimum_indep_vars_tuple, ut[0])
                cp.np_arr = linspace_around_value(
                    get_twotuple_value(minimum_indep_vars_tuple, ut[0]), *ut[1:])
                # print(np.size(cp.np_arr))

    return cparams_new
