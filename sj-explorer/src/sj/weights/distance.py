import logging
from libpysal.weights import DistanceBand, KNN
import libpysal

logger = logging.getLogger(__name__)

def create_distance_swm(geodf, threshold=1000, inverse=False):
    logger.info(f"--- Creating DistanceBand Matrix (Threshold: {threshold}m) ----")
    alpha = 1.0
    if inverse == True: alpha = -1.0
    distance_swm = DistanceBand.from_dataframe(geodf, threshold=threshold, alpha=alpha, use_index=True)

    return distance_swm

def create_knn_swm(geodf, k=4):
    logger.info("--- Creating KNN Matrix ----")
    knn_swm = KNN.from_dataframe(geodf, k=k, use_index=True)

    return knn_swm