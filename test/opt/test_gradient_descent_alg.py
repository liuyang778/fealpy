import pytest
import numpy as np
import warnings
from fealpy.backend import backend_manager as bm
from fealpy.opt.gradient_descent_alg import GradientDescentAlg
from fealpy.opt.optimizer_base import opt_alg_options

from gradient_descent_alg_data import *
from fealpy.opt.line_search_rules import *



class TestGradientDescentInterfaces:

    @pytest.mark.parametrize("backend", ['numpy','pytorch','jax'])
    @pytest.mark.parametrize("meshdata", init_data)
    def test_init(self,meshdata,backend):
        bm.set_backend(backend)
        x0 = bm.from_numpy(meshdata['x0'])
        objective = meshdata['objective']
        domain = bm.from_numpy(meshdata['domain'])
        NP  = meshdata['NP']
        MaxIters = meshdata['MaxIters']
        MaxFunEvals = meshdata['MaxFunEvals']
        NormGradTol = meshdata['NormGradTol']
        FunValDiff = meshdata['FunValDiff']
        StepLength = meshdata['StepLength']
        StepLengthTol = meshdata['StepLengthTol']
        NumGrad = meshdata['NumGrad']
        options = opt_alg_options(x0 = x0 ,
                                  objective = objective , 
                                  domain = domain,
                                  NP = NP, 
                                  MaxIters = MaxIters, 
                                  MaxFunEvals = MaxFunEvals,
                                  NormGradTol = NormGradTol, 
                                  FunValDiff = FunValDiff, 
                                  StepLength = StepLength, 
                                  StepLengthTol = StepLengthTol,
                                  NumGrad = NumGrad)
        GDA = GradientDescentAlg(options)
        options = GDA.options
        np.testing.assert_array_equal(bm.to_numpy(options['x0']), x0)
        np.testing.assert_array_equal(bm.to_numpy(options['domain']), domain)
        f , g = options['objective'](x0)
        assert f == objective(x0)[0]
        np.testing.assert_array_equal(bm.to_numpy( g) , objective(x0)[1])
        assert options['NP'] == NP
        assert options['MaxIters'] == MaxIters
        assert options['MaxFunEvals'] == MaxFunEvals
        assert options['NormGradTol'] == NormGradTol
        assert options['FunValDiff'] == FunValDiff
        assert options['StepLength'] == StepLength
        assert options['StepLengthTol'] == StepLengthTol
        assert options['NumGrad'] == NumGrad

    @pytest.mark.parametrize("backend", ['numpy','pytorch','jax'])
    @pytest.mark.parametrize("meshdata", run_data)
    @pytest.mark.parametrize("line_search_method", [
        ArmijoLineSearch(),
        PowellLineSearch(),
        GoldsteinLineSearch(),
        ZhangHagerLineSearch(),
        GrippoLineSearch(),
        ExactLineSearch(),
    ])

    def test_run(self,meshdata,backend,line_search_method):
        bm.set_backend(backend)
        x0 = bm.from_numpy(meshdata['x0'])
        objective = meshdata['objective']
        StepLength = meshdata['StepLength']
        MaxIters = meshdata['MaxIters']
        x1 = bm.from_numpy(meshdata['x'])
        f1 = meshdata['f']
        g1= bm.from_numpy(meshdata['g'])
        diff1 = bm.from_numpy(np.array(meshdata['diff']))
        
        # 忽略 DeprecationWarning
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        options = opt_alg_options(
            x0=x0,
            objective=objective,
            StepLength=StepLength,
            MaxIters=MaxIters,
            LineSearch = line_search_method
        )
        GDA = GradientDescentAlg(options)
        maxit = options['MaxIters']
        GDA = GradientDescentAlg(options)
        x , f ,g , diff = GDA.run(maxit=maxit)
        np.testing.assert_allclose(x, x1, atol=1e-6)
        np.testing.assert_allclose(f, f1 , atol=1e-6)
        np.testing.assert_allclose(g, g1 , atol=1e-6)
        np.testing.assert_allclose(diff, diff1 , atol= 1e-7)

if __name__ == "__main__":
    pytest.main(["./test_gradient_descent_alg.py","-k", "test_run"])
