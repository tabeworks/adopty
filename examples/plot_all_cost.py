import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from adopty.lista import Lista
from adopty.datasets import make_coding
from adopty.loss_and_gradient import cost_lasso


def get_c_star(x, D, z, reg, n_iter=10000, device=None):
    ista = Lista(D, n_iter, parametrization="coupled", device=device)
    return ista.score(x, reg, z0=z)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser('')
    parser.add_argument('--gpu', action='store_true',
                        help='Use GPU for training')
    args = parser.parse_args()

    device = 'cuda' if args.gpu else 'cpu'

    n_dim = 2
    n_atoms = 8
    n_samples = 10000

    x, D, z = make_coding(n_samples=n_samples, n_atoms=n_atoms, n_dim=n_dim)
    reg = .7
    n_layers = 3

    x_test = np.random.randn(*x.shape)

    format_cost = "{}: {} cost = {:.3e}"
    c_star = get_c_star(x, D, z, reg, device=device)

    saved_model = {}
    for parametrization in ['hessian', 'coupled']:
        lista = Lista(D, n_layers, parametrization=parametrization,
                      max_iter=3000, device=device)

        z_hat_test = lista.transform(x_test, reg)
        c_star_test = get_c_star(x_test, D, z_hat_test, reg, device=device)
        cost_test = cost_lasso(z_hat_test, D, x_test, reg) - c_star_test
        print(format_cost.format("Un-trained[{}]".format(parametrization),
                                 "test", cost_test))

        # Train and evaluate the network
        lista.fit(x, reg)
        z_hat_test = lista.transform(x_test, reg)
        c_star_test = get_c_star(x_test, D, z_hat_test, reg, device=device)
        cost_test = cost_lasso(z_hat_test, D, x_test, reg) - c_star_test
        print(format_cost.format("Trained[{}]".format(parametrization),
                                 "test", cost_test))
        saved_model[parametrization] = lista

        z_hat = lista.transform(x, reg)
        c_star = min(c_star, get_c_star(x, D, z_hat, reg, device=device))
        plt.loglog(lista.training_loss_ - c_star, label=parametrization)

    plt.legend()

    # Save the figure if it is not displayed
    if mpl.get_backend() == 'agg':
        plt.savefig("output.pdf", dpi=300)
    plt.show()