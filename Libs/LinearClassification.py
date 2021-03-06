import numpy as np
from sklearn.utils import shuffle

class Classification():
    def __init__(self, X, t, eta = 0.1, Nsegments = 5, Nepoch = 10, w0 = None, seed = None):
        self.N = len(t)
        self.t = t
        self.X = X
        self.D = len(X[0])
        self.Nclasses = len(t[0])
        self.eta = eta
        self.w = w0
        if self.w is None:
            if seed is not None: np.random.seed(seed)
            self.w = np.random.uniform(-5, 5, self.D*self.Nclasses)
        self.w = self.w.reshape(self.D, -1)

        self.Nsegments = Nsegments
        if self.N/Nsegments < 10:
            self.Nsegments = int(self.N/10)
        self.Nepoch = Nepoch
        self.NeachSegment = int(self.N / self.Nsegments)

    def _sigmoid(self, z):
        return 1.0/(1.0 + np.exp(-z))

    def __softmax(self, z):
        maxz = np.amax(z, axis = 1).reshape(-1, 1)
        expz = np.exp(z - maxz)
        tmp = np.sum(expz, axis = 1).reshape(-1, 1)
        return expz/tmp

    def _segmentation(self):
        for i in range(self.Nsegments):
            segX = self.X[i*self.NeachSegment:(i+1)*self.NeachSegment]
            segt = self.t[i*self.NeachSegment:(i+1)*self.NeachSegment]
            yield (segX, segt)

    def _shuffle(self):
        self.X, self.t = shuffle(self.X, self.t)

    def __fit(self, segmentX, segmentt):
        z = segmentX.dot(self.w)
        yhat = self.__softmax(z)
        deltaw = segmentX.T.dot(yhat - segmentt)
        self.w = self.w - self.eta*deltaw

    def _fit(self):
        self._shuffle()
        for segX, segt in self._segmentation():
            self.__fit(segX, segt)

    def fit(self):
        for i in range(self.Nepoch):
            self._fit()
        print("Training cross entropy = \n{}".format(self.trainCrossEntropy()))
        return self

    def _crossEntropy(self, t, prediction):
        tmp = - t * np.log(prediction + np.finfo(float).eps)
        return np.sum(tmp)

    def trainCrossEntropy(self):
        prediction = self._predict(self.X)
        return self._crossEntropy(self.t, prediction)

    def _predict(self, X, t = None):
        prediction = self.__softmax(X.dot(self.w))
        if t is not None:
            print("Cross entropy for prediction = \n{}".format(self._crossEntropy(t, prediction)))
        return prediction

    def predictLabel(self, X, t = None):
        prediction = self._predict(X, t)
        ret = np.argmax(prediction, axis = 1)
        return np.array(ret, dtype = float).reshape(-1, 1)

    def predict(self, X, t = None):
        prediction = self._predict(X, t)
        index = np.argmax(prediction, axis = 1)
        ret = []
        for i in range(len(index)):
            ret_ = np.zeros(self.Nclasses, dtype = float)
            ret_[index[i]] = 1.0
            ret.append(ret_)

        return np.array(ret)

class TwoClassesClassification(Classification):
    def __init__(self, X, t, eta = 0.1, Nsegments = 5, Nepoch = 10, w0 = None, seed = None):
        t = np.hstack((1 - t, t))
        super().__init__(X, t, eta, Nsegments, Nepoch, w0, seed)

    def predict(self, X, t = None):
        prediction = self._predict(X, t)
        tmp = np.heaviside(prediction - 0.5, 0.0)
        return tmp[:, 1].reshape(-1, 1)
