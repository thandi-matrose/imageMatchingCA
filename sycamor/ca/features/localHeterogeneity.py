from scipy.ndimage import uniform_filter
import numpy as np
from joblib import Parallel, delayed


def _divergence_tile(tile, window_size):
    mu    = uniform_filter(tile,         size=window_size, mode='reflect')
    mu_sq = uniform_filter(tile ** 2,    size=window_size, mode='reflect')
    variance = np.maximum(mu_sq - mu ** 2, 0)
    sigma = np.sqrt(variance)
    return np.divide(sigma, mu, out=np.zeros_like(sigma), where=mu != 0)


def getSpeckleDivergence(intensityBand, window_size: int = 9,
                         n_jobs: int = -1, n_tiles: int = 8):
    """
    Parallel version of the speckle-divergence map D = sigma / mu.
    Splits rows into overlapping strips, computes in parallel, then crops.
    """
    h, w = intensityBand.shape
    margin = window_size // 2 + 1              # +1 for reflect safety

    # Build (y0, y1, y0_ext, y1_ext) strips
    rows_per_tile = int(np.ceil(h / n_tiles))
    strips = []
    for i in range(n_tiles):
        y0 = i * rows_per_tile
        y1 = min(h, y0 + rows_per_tile)
        if y0 >= y1:
            continue
        strips.append((y0, y1, max(0, y0 - margin), min(h, y1 + margin)))

    results = Parallel(n_jobs=n_jobs, prefer="threads")(
        delayed(_divergence_tile)(intensityBand[y0e:y1e, :], window_size)
        for (_, _, y0e, y1e) in strips
    )

    out = np.empty(intensityBand.shape, dtype=np.float64)
    for (y0, y1, y0e, _), res in zip(strips, results):
        top = y0 - y0e
        out[y0:y1, :] = res[top:top + (y1 - y0), :]

    return out