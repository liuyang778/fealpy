from fealpy.backend import backend_manager as bm
from scipy.special import gamma
from .chaos import *

import time
def levy(n, m, beta):
    """
    Levy flight
    """
    num = gamma(1 + beta) * bm.sin(bm.array(bm.pi * beta / 2))
    den = gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2)
    sigma_u = (num / den) ** (1 / beta)
    u = bm.random.randn(n, m) * sigma_u
    v = bm.random.randn(n, m)
    z = u / (bm.abs(v) ** (1 / beta))
    return z

def initialize(pop_size, dim, ub, lb, method=None):
    """
    Initialize a population with various method maps.

    Parameters:
    -----------
    pop_size : int
        Number of individuals in the population.
    dim : int
        Number of dimensions for each individual.
    ub : list
        Upper bounds for each dimension. Must be a list of length `dim`.
    lb : list
        Lower bounds for each dimension. Must be a list of length `dim`.
    method : callable, optional, default=None
        A function defining the chaotic map to generate the population.
        If None, a random distribution is used for initialization.

    Returns:
    --------
    pop : Tensor
        Initialized population of shape (pop_size, dim).
    """

    if isinstance(ub, (list, tuple)) and isinstance(lb, (list, tuple)):
        if len(ub) != dim or len(lb) != dim:
            raise ValueError(f"Lengths of 'ub' and 'lb' must match 'dim'. "
                             f"Received: len(ub)={len(ub)}, len(lb)={len(lb)}, dim={dim}")
    elif not isinstance(ub, (float, int)) or not isinstance(lb, (float, int)):
        raise TypeError("Both 'ub' and 'lb' must be either scalars or lists/tuples of length 'dim'.")
    

    pop = bm.zeros([pop_size, dim])
    if method == None:
        rand = bm.random.rand(pop_size, dim)
    else:
        rand = method(pop_size, dim)

    if isinstance(ub, (float, int)):
            pop = lb + rand * (ub - lb)
    else:
        for i in range(dim):
            pop[:, i] = rand[:, i] * (ub[i] - lb[i]) + lb[i]    
    
    return pop

def PathPlanning(MAP, dataS, dataE, method):
    start_time = time.perf_counter()
    from fealpy.opt.particle_swarm_opt_alg import PathPlanningProblem, PSO, QPSO
    from fealpy.opt import initialize, opt_alg_options
    if MAP[dataS[0]][dataS[1]] != 0 or MAP[dataE[0]][dataE[1]] != 0: 
        print("Error: Wrong start point or end point") # 判断起点终点坐标是否有效
    else:
        textMAP = PathPlanningProblem(MAP, dataS, dataE)
        textMAP.builddata() # 建立地图字典
        fobj = lambda x: textMAP.fitness(x)
        
        # 算法参数
        N = 20
        MaxIT = 50
        lb = 0
        ub = 1
        dim = textMAP.data["landmark"].shape[0]
        
        # 调用算法
        xo = initialize(N, dim, ub, lb)
        option = opt_alg_options(xo, fobj, (lb, ub), N, MaxIters=MaxIT)
        optimizer = method(option)
        optimizer.run()
        
        result = textMAP.calresult(optimizer.gbest)
        
        # 输出
        result["path"] = [x for x, y in zip(result["path"], result["path"][1:] + [None]) if x != y]
        print('The optimal path distance: ', optimizer.gbest_f)
        print("The optimal path: ", result["path"])
        end_time = time.perf_counter()
        running_time = end_time - start_time
        textMAP.printMAP(result, running_time)
