
from abc import ABCMeta
from typing import(
    Union, Optional, Dict, Iterable, Tuple, List, Any, Type, Generic, TypeVar,
    Hashable, OrderedDict, overload
)
from math import comb

from .. import logger


Size = Tuple[int, ...]

class TensorLike(metaclass=ABCMeta):
    @property
    def dtype(self) -> Any: raise NotImplementedError
    @property
    def device(self) -> Any: raise NotImplementedError
    @property
    def mT(self) -> 'TensorLike': raise NotImplementedError
    @property
    def ndim(self) -> int: raise NotImplementedError
    @property
    def shape(self) -> Tuple[int, ...]: raise NotImplementedError
    @property
    def size(self) -> int: raise NotImplementedError
    @property
    def T(self) -> 'TensorLike': raise NotImplementedError

    def __len__(self) -> int: raise NotImplementedError
    def __getitem__(self, index: Any) -> 'TensorLike': raise NotImplementedError
    @overload
    def reshape(self, newshape: Size, /) -> 'TensorLike': raise NotImplementedError
    @overload
    def reshape(self, *newshape: int) -> 'TensorLike': raise NotImplementedError
    def reshape(self, *newshape) -> 'TensorLike': raise NotImplementedError


Number = Union[int, float]
_DT = TypeVar("_DT")


# NOTE: WHAT ARE THE NAMES LISTED BELOW?
#
# These are mappings with names of attributes and functions in fealpy backend as keys,
# and the values are the corresponding names in the backend such as numpy.
#
#   - If a functions is NOT defined in the subclass of Backend (the base), FEALPy will try to
#     copy the function from the backend according to the mapping.
#
#   - Each mapping have a format of {target_name: source_name}. Where `target_name` is
#     how we call the function or attribute in FEALPy, while `source_name` is the original
#     name in the backend.
#
#   - For example, the mapping {'transpose': 'permute'} means that the function `transpose` in
#     FEALPy will be copied from the function `permute` in the backend, and we can
#     use `backend_manager.transpose(x)` to use the `permute` function.
#
#   - The names below are actually the target names. Using the function `_make_default_mapping`,
#     a default mapping is created with the SAME source names.
#     These default mappings will be imported by the Backend subclasses and
#     may be updated to adapt to the backend.


def _make_default_mapping(*names: str):
    return {k: k for k in names}


# NOTE: To add new attributes, just add the target names here, then for each
# backend, see if the names are supported.
# Update the source name in the backend file if necessary.
#
ATTRIBUTE_MAPPING = _make_default_mapping(
    # Constants
    'pi', 'e', 'nan', 'inf', 'newaxis',
    'dtype', 'device',
    # Dtype
    'bool',
    'uint8', 'uint16', 'uint32', 'uint64',
    'int8', 'int16', 'int32', 'int64',
    'float16', 'float32', 'float64',
    'complex64', 'complex128',
)

# NOTE: For adding new functions:
#
# 1. Add the target function names in the correct category.
#
# 2. Go to the stub file and add typehints for the functions.
#    (define the args and return of the function)
#
# 3. For each backend, see if the functions we expected are supported. There may be some cases:
#
#    - Not supported: implement manually.
#    - Supported, but with different names: update the source name in the backend file.
#    - Supported, but the args or returns are in different format: make a wrapper function
#      in the backend subclass.
#    - Totally the same: nothing need to do.
#
FUNCTION_MAPPING = _make_default_mapping(

    ### Creation Functions ###
    # python array API standard v2023.12
    'array',
    'asarray',
    'arange', 'linspace',
    'empty', 'zeros', 'ones', 'full',
    'empty_like', 'zeros_like', 'ones_like', 'full_like',
    'eye', 'meshgrid',
    'tril', 'triu',

    # non-standard
    'tensor',

    ### Data Type Functions ###
    # python array API standard v2023.12
    'astype', 'can_cast',
    'finfo', 'iinfo',
    'isdtype', 'result_type',

    ### Element-wise Functions ###
    # python array API standard v2023.12
    'abs', 'acos', 'acosh', 'add', 'asin', 'asinh', 'atan', 'atan2', 'atanh',
    'bitwise_and', 'bitwise_left_shift', 'bitwise_invert', 'bitwise_or',
    'bitwise_right_shift', 'bitwise_xor',
    'ceil', 'clip', 'conj', 'copysign', 'cos', 'cosh',
    'divide',
    'equal', 'exp', 'expm1',
    'floor', 'floor_divide',
    'greater', 'greater_equal',
    'hypot', 
    'imag', 'isfinite', 'isinf', 'isnan',
    'less', 'less_equal', 'log', 'log1p', 'log2', 'log10', 'logaddexp', 'logical_and',
    'logical_not', 'logical_or', 'logical_xor',
    'maximum', 'minimum', 'multiply',
    'negative', 'not_equal',
    'positive', 'pow',
    'real', 'remainder', 'round',
    'sign', 'signbit', 'sin', 'sinh', 'square', 'sqrt', 'subtract',
    'tan', 'tanh', 'trunc',

    # non-standard
    'arcsin', 'arccos', 'arctan', 'arctan2', 'arcsinh', 'arccosh', 'arctanh',
    'power',

    ### Indexing Functions ###
    # python array API standard v2023.12
    'take',

    ### Inspection ###
    # python array API standard v2023.12
    # non-standard

    ### Linear Algebra Functions ###
    # python array API standard v2023.12
    'matmul', 'matrix_transpose', 'tensordot',
    'vecdot',
    # non-standard
    'cross', 'cumsum', 'cumprod',
    'dot', 'einsum',

    ### Manipulation Functions ###
    # python array API standard v2023.12
    'broadcast_arrays', 'broadcast_to',
    'concat',
    'expand_dims',
    'flip',
    'moveaxis',
    'permute_dims',
    'repeat', 'reshape', 'roll',
    'squeeze', 'stack',
    'tile',
    'unstack',
    # non-standard
    'concatenate', 'swapaxes', 'transpose',

    ### Searching Functions ###
    # python array API standard v2023.12
    'argmax', 'argmin', 'nonzero', 'searchsorted', 'where',

    ### Set Functions ###
    # python array API standard v2023.12
    'unique_all', 'unique_counts', 'unique_inverse', 'unique_values',

    # non-standard
    'setdiff1d',
    'unique',

    ### Sorting Functions ###
    # python array API standard v2023.12
    'argsort', 'sort',

    ### Statistical Functions ###
    # python array API standard v2023.12
    'cumulative_sum',
    'max', 'mean', 'min',
    'prod',
    'std', 'sum',
    'var',
    # non-standard

    ### Utility Functions ###
    # python array API standard v2023.12
    'all', 'any',
    # non-standard
    'allclose',
    'copy',
    'size',

    ### Functional programming ###
    'apply_along_axis',
)


class Backend(Generic[_DT]):
    """
    Base class for all backends.
    """
    DATA_CLASS: Optional[Type[_DT]] = None
    _available_backends: Dict[str, Type["Backend"]] = {}

    def __init_subclass__(cls, backend_name: str, **kwargs):
        super().__init_subclass__(**kwargs)

        if backend_name != "":
            cls._available_backends[backend_name.lower()] = cls
            cls.backend_name = backend_name
            TensorLike.register(cls.DATA_CLASS)
        else:
            raise ValueError("Backend name cannot be empty.")

    @classmethod
    def attach_attributes(cls, mapping: Dict[str, str], source: Any):
        for target_key, source_key in mapping.items():
            if (source_key is None) or (source_key == ''):
                continue
            if hasattr(source, source_key):
                setattr(cls, target_key, getattr(source, source_key))

    @classmethod
    def attach_methods(cls, mapping: Dict[str, str], source: Any):
        for target_key, source_key in mapping.items():
            if (source_key is None) or (source_key == ''):
                continue
            if hasattr(cls, target_key):
                # Methods will not be copied from source if implemented manually.
                logger.debug(f"`{target_key}` already defined. "
                             f"Skip the copy from {source.__name__}.")
                continue
            if hasattr(source, source_key):
                setattr(cls, target_key, staticmethod(getattr(source, source_key)))
            else:
                logger.warning(f"`{source_key}` not found in {source.__name__}. "
                               f"Method `{target_key}` remains unimplemented.")

    @classmethod
    def show_unsupported(cls, signal: bool, function_name: str, arg_name: str) -> None:
        if signal:
            logger.warning(f"{cls.__name__} does not support the "
                           f"'{arg_name}' argument in the function {function_name}. "
                           f"The argument will be ignored.")

    @classmethod
    def is_tensor(cls, obj: Any, /) -> bool:
        return isinstance(obj, cls.DATA_CLASS)

    ### FEALPy functionals ###

    @staticmethod
    def simplex_ldof(p: int, iptype: int) -> int:
        if iptype == 0:
            return 1
        return comb(p + iptype, iptype)

    @staticmethod
    def simplex_gdof(p: int, nums: Tuple[int, ...]) -> int:
        coef = 1
        count = nums[0]

        for i in range(1, len(nums)):
            coef = (coef * (p-i)) // i
            count += coef * nums[i]
        return count

    @staticmethod
    def tensor_ldof(p: int, iptype: int) -> int:
        return (p + 1) ** iptype

    @staticmethod
    def tensor_gdof(p: int, nums: Tuple[int, ...]) -> int:
        coef = 1
        count = nums[0]
        for i in range(1, len(nums)):
            coef *= (p-1)
            count += coef * nums[i]
        return count

    @staticmethod
    def occurrence(iterable: Iterable[Hashable], /) -> Tuple[List[Hashable], List[int], List[int]]:
        # TODO: Implement a C version for higher performance.
        first = OrderedDict()
        last = OrderedDict()

        for i, item in enumerate(iterable):
            if item not in first:
                first[item] = i
            last[item] = i

        return list(first.keys()), list(first.values()), list(last.values())
