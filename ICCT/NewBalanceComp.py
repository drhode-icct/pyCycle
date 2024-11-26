from openmdao.api import ImplicitComponent
import numpy as np
from openmdao.utils.cs_safe import abs as cs_abs
from openmdao.utils.general_utils import shape_to_len

class NewBalanceComp(ImplicitComponent):
    """
    A simple equation balance for solving implicit equations, modified to allow constants on either side.

    Parameters
    ----------
    name : str
        The name of the state variable to be created.
    eq_units : str or None
        Units for the left-hand-side and right-hand-side of the equation to be balanced.
    lhs_name : str or None
        Optional name for the LHS variable associated with the implicit state variable. If
        None, the default will be used: 'lhs:{name}'.
    rhs_name : str or None
        Optional name for the RHS variable associated with the implicit state variable. If
        None, the default will be used: 'rhs:{name}'.
    lhs_val : int, float, or np.array, optional
        Constant value for the LHS of the equation. If provided, no input will be created for LHS.
    rhs_val : int, float, or np.array, optional
        Constant value for the RHS of the equation. If provided, no input will be created for RHS.
    use_mult : bool
        Specifies whether the LHS multiplier is to be used. If True, then an additional
        input `mult_name` is created, with the default value given by `mult_val`, that
        multiplies lhs. Default is False.
    mult_name : str or None
        Optional name for the LHS multiplier variable associated with the implicit state
        variable. If None, the default will be used: 'mult:{name}'.
    mult_val : int, float, or np.array
        Default value for the LHS multiplier of the given state. Must be compatible
        with the shape (optionally) given by the val or shape option in kwargs.
    normalize : bool
        Specifies whether or not the resulting residual should be normalized by a quadratic
        function of the RHS.
    val : float, int, or np.ndarray
        Set initial value for the state.
    **kwargs : dict
        Additional arguments to be passed for the creation of the implicit state variable.
        (see `add_output` method).

    Attributes
    ----------
    _state_vars : dict
        Cache the data provided during `add_balance` so everything can be saved until setup is called.
    """

    def initialize(self):
        """
        Declare options.
        """
        self.options.declare('guess_func', default=None,
                             desc='A callable function that can provide an initial guess '
                                  'for the state variable(s) based on the inputs, outputs, '
                                  'and residuals.')

    def __init__(self, name=None, eq_units=None, lhs_name=None, rhs_name=None, lhs_val=None,
                 rhs_val=None, use_mult=False, mult_name=None, mult_val=1.0, normalize=True,
                 val=None, **kwargs):
        super().__init__()

        self._state_vars = {}

        if name is not None:
            self.add_balance(name, eq_units=eq_units, lhs_name=lhs_name, rhs_name=rhs_name,
                             lhs_val=lhs_val, rhs_val=rhs_val, use_mult=use_mult,
                             mult_name=mult_name, mult_val=mult_val, normalize=normalize,
                             val=val, **kwargs)

    def add_balance(self, name, eq_units=None, lhs_name=None, rhs_name=None, lhs_val=None,
                    rhs_val=None, use_mult=False, mult_name=None, mult_val=1.0, normalize=True,
                    val=None, **kwargs):
        """
        Add a new state variable and associated equation to be balanced.

        Parameters
        ----------
        name : str
            The name of the state variable to be created.
        eq_units : str or None
            Units for the left-hand-side and right-hand-side of the equation to be balanced.
        lhs_name : str or None
            Optional name for the LHS variable associated with the implicit state variable. If
            None, the default will be used: 'lhs:{name}'.
        rhs_name : str or None
            Optional name for the RHS variable associated with the implicit state variable. If
            None, the default will be used: 'rhs:{name}'.
        lhs_val : int, float, or np.array, optional
            Constant value for the LHS of the equation. If provided, no input will be created for LHS.
        rhs_val : int, float, or np.array, optional
            Constant value for the RHS of the equation. If provided, no input will be created for RHS.
        use_mult : bool
            Specifies whether the LHS multiplier is to be used. If True, then an additional
            input `mult_name` is created, with the default value given by `mult_val`, that
            multiplies lhs. Default is False.
        mult_name : str or None
            Optional name for the LHS multiplier variable associated with the implicit state
            variable. If None, the default will be used: 'mult:{name}'.
        mult_val : int, float, or np.array
            Default value for the LHS multiplier. Must be compatible with the shape (optionally)
            given by the val or shape option in kwargs.
        normalize : bool
            Specifies whether or not the resulting residual should be normalized by a quadratic
            function of the RHS.
        val : float, int, or np.ndarray
            Set initial value for the state.
        **kwargs : dict
            Additional arguments to be passed for the creation of the implicit state variable.
            (see `add_output` method).
        """
        options = {'kwargs': kwargs,
                   'eq_units': eq_units,
                   'lhs_name': lhs_name,
                   'rhs_name': rhs_name,
                   'lhs_val': lhs_val,
                   'rhs_val': rhs_val,
                   'use_mult': use_mult,
                   'mult_name': mult_name,
                   'mult_val': mult_val,
                   'normalize': normalize}

        self._state_vars[name] = options

        if val is None:
            # If user doesn't specify initial guess for val, we can size problem from initial
            # rhs_val or lhs_val.
            if 'shape' not in kwargs:
                if rhs_val is not None and np.ndim(rhs_val) > 0:
                    kwargs['shape'] = np.shape(rhs_val)
                elif lhs_val is not None and np.ndim(lhs_val) > 0:
                    kwargs['shape'] = np.shape(lhs_val)

        else:
            options['kwargs']['val'] = val

        meta = self.add_output(name, **options['kwargs'])

        shape = meta['shape']

        for s in ('lhs', 'rhs', 'mult'):
            if options['{0}_name'.format(s)] is None:
                options['{0}_name'.format(s)] = '{0}:{1}'.format(s, name)

        # Add inputs for lhs and rhs if they are not constants
        if lhs_val is None:
            self.add_input(options['lhs_name'],
                           val=np.ones(shape),
                           units=options['eq_units'])
        else:
            # Ensure lhs_val is an array of correct shape
            options['lhs_val'] = np.full(shape, lhs_val)

        if rhs_val is None:
            self.add_input(options['rhs_name'],
                           val=np.ones(shape),
                           units=options['eq_units'])
        else:
            # Ensure rhs_val is an array of correct shape
            options['rhs_val'] = np.full(shape, rhs_val)

        if options['use_mult']:
            if options['mult_name'] is None:
                options['mult_name'] = 'mult:{0}'.format(name)
            self.add_input(options['mult_name'],
                           val=options['mult_val'] * np.ones(shape),
                           units=None)

        ar = np.arange(shape_to_len(shape))

        # Declare partials only for variables that are inputs
        if lhs_val is None:
            self.declare_partials(of=name, wrt=options['lhs_name'], rows=ar, cols=ar)
        if rhs_val is None:
            self.declare_partials(of=name, wrt=options['rhs_name'], rows=ar, cols=ar)
        if options['use_mult']:
            self.declare_partials(of=name, wrt=options['mult_name'], rows=ar, cols=ar)

    def apply_nonlinear(self, inputs, outputs, residuals):
        """
        Calculate the residual for each balance.

        Parameters
        ----------
        inputs : Vector
            Unscaled, dimensional input variables read via inputs[key].
        outputs : Vector
            Unscaled, dimensional output variables read via outputs[key].
        residuals : Vector
            Unscaled, dimensional residuals written to via residuals[key].
        """
        for name, options in self._state_vars.items():
            # Get lhs
            if options['lhs_val'] is not None:
                lhs = options['lhs_val']
            else:
                lhs = inputs[options['lhs_name']]

            # Get rhs
            if options['rhs_val'] is not None:
                rhs = options['rhs_val']
            else:
                rhs = inputs[options['rhs_name']]

            # Set scale factor
            _scale_factor = np.ones(rhs.shape, dtype=rhs.dtype)

            if options['normalize']:
                # Indices where the rhs is near zero or not near zero
                idxs_nz = np.where(cs_abs(rhs) < 2)
                idxs_nnz = np.where(cs_abs(rhs) >= 2)

                # Compute scaling factors
                _scale_factor[idxs_nnz] = 1.0 / cs_abs(rhs[idxs_nnz])
                _scale_factor[idxs_nz] = 1.0 / (0.25 * rhs[idxs_nz] ** 2 + 1)

            if options['use_mult']:
                mult = inputs[options['mult_name']]
                residuals[name] = (mult * lhs - rhs) * _scale_factor
            else:
                residuals[name] = (lhs - rhs) * _scale_factor

    def linearize(self, inputs, outputs, jacobian):
        """
        Calculate the partials of the residual for each balance.

        Parameters
        ----------
        inputs : Vector
            Unscaled, dimensional input variables read via inputs[key].
        outputs : Vector
            Unscaled, dimensional output variables read via outputs[key].
        jacobian : Jacobian
            Sub-jac components written to jacobian[output_name, input_name].
        """
        for name, options in self._state_vars.items():
            # Get lhs
            if options['lhs_val'] is not None:
                lhs = options['lhs_val']
            else:
                lhs = inputs[options['lhs_name']]

            # Get rhs
            if options['rhs_val'] is not None:
                rhs = options['rhs_val']
            else:
                rhs = inputs[options['rhs_name']]

            _scale_factor = np.ones(rhs.shape, dtype=rhs.dtype)
            _dscale_drhs = np.zeros(rhs.shape, dtype=rhs.dtype)

            if options['normalize']:
                idxs_nz = np.where(cs_abs(rhs) < 2)
                idxs_nnz = np.where(cs_abs(rhs) >= 2)

                _scale_factor[idxs_nnz] = 1.0 / cs_abs(rhs[idxs_nnz])
                _scale_factor[idxs_nz] = 1.0 / (0.25 * rhs[idxs_nz] ** 2 + 1)

                _dscale_drhs[idxs_nnz] = -np.sign(rhs[idxs_nnz]) / rhs[idxs_nnz] ** 2
                _dscale_drhs[idxs_nz] = -0.5 * rhs[idxs_nz] / (0.25 * rhs[idxs_nz] ** 2 + 1) ** 2

            if options['use_mult']:
                mult = inputs[options['mult_name']]
            else:
                mult = 1.0

            # Compute derivatives
            if options['lhs_val'] is None:
                deriv_lhs = mult * _scale_factor
                jacobian[name, options['lhs_name']] = deriv_lhs.flatten()

            if options['rhs_val'] is None:
                deriv_rhs = (mult * lhs - rhs) * _dscale_drhs - _scale_factor
                jacobian[name, options['rhs_name']] = deriv_rhs.flatten()

            if options['use_mult']:
                deriv_mult = lhs * _scale_factor
                jacobian[name, options['mult_name']] = deriv_mult.flatten()

    def guess_nonlinear(self, inputs, outputs, residuals):
        """
        Provide initial guess for states.

        Parameters
        ----------
        inputs : Vector
            Unscaled, dimensional input variables read via inputs[key].
        outputs : Vector
            Unscaled, dimensional output variables read via outputs[key].
        residuals : Vector
            Unscaled, dimensional residuals written to via residuals[key].
        """
        if self.options['guess_func'] is not None:
            self.options['guess_func'](inputs, outputs, residuals)