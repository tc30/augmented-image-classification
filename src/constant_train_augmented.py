from IPython.display import display
from ipywidgets import FloatProgress

import neuralnetworkclassifier as nnc
import dataset_manipulations as dm
import mlutils as ml
import perturb as per
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.pylab as pl

from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
rc('text', usetex=True)
plt.style.use('seaborn-whitegrid')

######################################################################

COLORS = pl.cm.Set2(np.linspace(0, 1, 8))

######################################################################

def augmented_training(Xtrain, Ttrain, Xtest, Ttest, type='pixel', model='MNIST', technique="constant"):

    if type == 'pixel':
        perturbs = ['stuck', 'dead', 'hot']
        training_vals = np.arange(1, 11)
        test_types = perturbs
        xlabel = 'Num Training Pixel(s)'
        test_pixel_change = 2
    else:
        perturbs = ['noise']
        training_vals = np.linspace(0.001, 0.05, 5)
        test_types = [0.02550, 0.03775, 0.05000]
        xlabel = 'Training Variance of Noise'

    trials = 1

    f = FloatProgress(min=0, max=(len(perturbs) * len(training_vals) * (trials * len(test_types))))
    display(f)

    for i, perturb in enumerate(perturbs):

        natural_acc = []
        augmented_acc = np.zeros((len(test_types), 2, len(training_vals)))

        """
        test_perturb_1

               p_1 p_2 p_3 p_4
        mean [[0., 0., 0., 0.],
        std   [0., 0., 0., 0.]],

        test_perturn_2
        ...

        """

        for p, val in enumerate(training_vals):

            if type == 'pixel':
                Mtrain = per.change_pixel(Xtrain, pixels_to_change=val+1, pertrub=perturb)
            else:
                Mtrain = per.add_image_noise(Xtrain, val)

            if model == 'MNIST':
                if(technique == 'incremental'):
                    nnet = per.train_incremental_mnist(Xtrain, Ttrain, Mtrain)

                elif(technique == 'transfer'):
                    nnet = per.train_cifar(Mtrain, Ttrain)

                else:
                    nnet = per.train_mnist(Mtrain, Ttrain)
            else:
                if(technique == 'incremental'):
                    nnet = per.train_incremental_cifar(Xtrain, Ttrain, Mtrain)

                elif(technique == 'transfer'):
                    nnet = per.train_cifar(Mtrain, Ttrain)

                else:
                    nnet = per.train_cifar(Mtrain, Ttrain)

            print('Finished training a model...', flush=True)

            natural_acc.append(ml.percent_correct(ml.batched_use(nnet, Xtest), Ttest))

            for t, test_perturb in enumerate(test_types):

                tmp = []

                for trial in range(trials):
                    if type == 'pixel':
                        M = per.change_pixel(Xtest, pixels_to_change=test_pixel_change, pertrub=test_perturb)
                    else:
                        M = per.add_image_noise(Xtest, test_perturb)
                    tmp.append(ml.percent_correct(ml.batched_use(nnet, M), Ttest))
                    f.value += 1

                augmented_acc[t, 0, p] = np.mean(tmp)
                augmented_acc[t, 1, p] = np.std(tmp)

        print('finished testing: ', perturb, flush=True)

        plt.figure(figsize=(6, 4))

        for t, test_perturb in enumerate(test_types):
            if type == 'pixel':
                label = test_perturb
            else:
                label=f'{test_perturb:.5f}'
            plt.errorbar(training_vals, augmented_acc[t, 0], yerr=augmented_acc[t, 1],
                         marker='.', lw=1, capsize=5, capthick=1.5, label=label,
                         markeredgecolor='k', color=COLORS[t])

        plt.plot(training_vals, natural_acc, marker='.', lw=1, label=f'natural',
                 markeredgecolor='k', color=COLORS[3])

        plt.xticks(training_vals)
        plt.xlabel(xlabel)
        plt.ylabel('Accuracy ( \% )')
        plt.legend(loc='best', fontsize='large')
        plt.grid(True); plt.tight_layout();
        plt.savefig('../notebooks/media/'+ technique +'/' + model.lower() + '-' + type
                    + '-' + perturb + '.pdf', bbox_inches='tight')
        # plt.show();

if __name__ == '__main__':

    print('Loading MNIST data', flush=True)
    Xtrain, Ttrain, Xtest, Ttest, _, _ = dm.load_mnist('../notebooks/mnist.pkl.gz')
    print('Done loading MNIST data', flush=True)

    #augmented_training(Xtrain, Ttrain, Xtest, Ttest, type='pixel', model='MNIST', technique='constant')
    #augmented_training(Xtrain, Ttrain, Xtest, Ttest, type='noise', model='MNIST', technique='constant')

    #augmented_training(Xtrain, Ttrain, Xtest, Ttest, type='pixel', model='MNIST', technique='incremental')
    augmented_training(Xtrain, Ttrain, Xtest, Ttest, type='noise', model='MNIST', technique='incremental')

    print('Loading CIFAR data', flush=True)
    Xtrain, Ttrain = dm.load_cifar_10('../notebooks/cifar-10-batches-py/data_batch_*')
    Xtest, Ttest = dm.load_cifar_10('../notebooks/cifar-10-batches-py/test_batch')
    print('Done loading CIFAR data', flush=True)

    #augmented_training(Xtrain, Ttrain, Xtest, Ttest, type='pixel', model='CIFAR', technique='constant')
    #augmented_training(Xtrain, Ttrain, Xtest, Ttest, type='noise', model='CIFAR', technique='constant')

    #augmented_training(Xtrain, Ttrain, Xtest, Ttest, type='pixel', model='CIFAR', technique='incremental')
    #augmented_training(Xtrain, Ttrain, Xtest, Ttest, type='noise', model='CIFAR', technique='incremental')

    print('Finished Trial', flush=True)