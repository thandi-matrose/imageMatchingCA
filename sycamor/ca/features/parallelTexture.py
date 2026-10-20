import numpy as np
from skimage.feature import graycomatrix, graycoprops
from skimage.util import view_as_windows
from joblib import Parallel, delayed

from sycamor.ca.features.logIntensity import getLogIntensity
from sycamor.ca.features.set import Feature
from sycamor.retrieval import dataset
from sycamor.visualisation.plot import distributionFeature

levels       = 64
WINDOW_SIZE  = 15
angles       = [0,  np.pi / 2, ]
props        = ['energy', 'mean', 'variance']


class TextureAnalyser:

    def __init__(self, intensityData):
        self.intensityData = intensityData
        self.quantize()

    @staticmethod
    def _process_windows(windows, levels):
        """windows : (N, window_size, window_size) uint8 → (N, len(props)) float"""
        out = np.empty((windows.shape[0], len(props)), dtype=np.float64)
        for i, win in enumerate(windows):
            glcm = graycomatrix(
                win,
                distances=[1],
                angles=angles,
                levels=levels,
                symmetric=True,
                normed=True,
            )
            for j, prop in enumerate(props):
                out[i, j] = np.mean(graycoprops(glcm, prop))
        return out

    def calculateGLCM(self, n_jobs: int = -1, chunk: int = 256):
        # 1. Extract every sliding window in one shot (view, no copy)
        windows = view_as_windows(
            self.intensityData, (WINDOW_SIZE, WINDOW_SIZE)
        )                                      # (H', W', ws, ws)
        H, W = windows.shape[:2]
        flat = windows.reshape(-1, WINDOW_SIZE, WINDOW_SIZE)
        
        # 2. Split into chunks and dispatch
        chunks = [flat[i:i + chunk] for i in range(0, flat.shape[0], chunk)]
        results = Parallel(n_jobs=n_jobs, prefer="processes")(
            delayed(self._process_windows)(c, levels) for c in chunks
        )

        stacked = np.vstack(results).reshape(H, W, len(props))

        return {prop: stacked[..., i] for i, prop in enumerate(props)}

    def quantize(self):
        normalized = self.intensityData / 25
        quantized  = normalized * (levels - 1)
        self.intensityData = np.round(quantized).astype(np.uint8)