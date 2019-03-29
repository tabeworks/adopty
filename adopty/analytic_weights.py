import numpy as np


def obj_func(W, D):
    """Cost function to minimize to obtain the analytic weights

    Parameters
    ----------
    D : ndarray, shape (n_atoms, n_dim)
        Dictionary for the considered sparse coding problem.
    """
    n_atoms, n_dim = D.shape
    Ik = np.eye(n_atoms)
    WtD = W.dot(D.T) - Ik
    Q = np.ones((n_atoms, n_atoms)) - Ik
    WtD *= np.sqrt(Q)
    return np.sum(WtD * WtD)


def proj(W, D):
    """Projection for W on the constraint set s.t. W_i^TD_i = 1
    """
    aw = np.diag(W.dot(D.T))
    return W + (1-aw)[:, None] * D


def get_alista_weights(D, max_iter=10000, step_size=1e-1, tol=1e-8):
    """Cost function to minimize to obtain the analytic weights

    Parameters
    ----------
    D : ndarray, shape (n_atoms, n_dim)
        Dictionary for the considered sparse coding problem.
    """
    n_atoms, n_dim = D.shape
    W = np.copy(D)
    pobj = [obj_func(W, D)]
    for i in range(max_iter):
        res = W.dot(D.T) - np.eye(n_atoms)
        grad = res.dot(D)
        W -= step_size * grad

        W = proj(W, D)

        pobj.append(obj_func(W, D))
        assert pobj[-1] <= pobj[-2]
        if 1 - pobj[-1] / pobj[-2] < tol:
            break

    assert np.allclose(np.diag(W.dot(D.T)), 1)
    return W