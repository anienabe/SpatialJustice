# weight one matrix according to index
# do children with migration backgrounds cluster among neighborhoods that are structurally similar in poverty?

# requirements
# socioWeight

import logging
import numpy as np
from enum import Enum
from libpysal.weights import W as WObject

logger = logging.getLogger(__name__)

class SocioWeight(Enum):
    """Encondes the desired assumptions of connectivity
    Similarity: assumes that spatial processes propagate through shared social conditions.
    Gradient: The larger the difference, the stronger the connection.
    Neighborhoods that contrast sharply are considered more strongly related.
    Product: Only the most deprived neighborhoods form a meaningful network
 
    Args:
        Enum (_type_): What type or proximity method should be considered
 
    Returns:
        None
    """

    SIMILARITY = "similarity" # similar places connect more
    GRADIENT = "gradient" # contrasting places connect more
    PRODUCT = "product" # both need to be high

def create_socio_swm(
    geodf,
    base_w: WObject,
    index_col: str,
    method: SocioWeight = SocioWeight.SIMILARITY,
):
    """
    Takes an existing libpysal W object and re-weights its edges
    using a socioeconomic index column from the GeoDataFrame.

    base_w defines WHO is connected (Rook, Queen, etc.)
    method defines HOW STRONGLY, based on the socioeconomic index.

    Args:
        geodf:     GeoDataFrame with the socioeconomic attribute column.
        base_w:    A libpysal W object (Rook, Queen, or any other base structure).
        index_col: Column name in geodf to use as the socioeconomic index.
        method:    SocioWeight enum value defining the weighting function.

    Returns:
        A new libpysal W object with the same neighbor structure as base_w
        but with socioeconomically-derived edge weights, row-standardized.
    """
    logger.info(
        f"Creating Socioeconomic SWM — base: {type(base_w).__name__}, method: {method.value}, index: {index_col}"
    )

    # extract and normalize the socioeconomic index to [0,1]
    raw_values = geodf[index_col].values.astype(float)
    min_val = raw_values.min()
    max_val = raw_values.max()

    if max_val == min_val:
        raise ValueError(f"Column '{index_col}' has zero variance — cannot normalize.")
    # WHY WE NEED THIS? Oh my... I am lost... :(
    # Because we need a way to compare % variables
    normalized_index = (raw_values - min_val) / (max_val - min_val)

    new_weights = {}

    for i, neighbors in base_w.neighbors.items():
        raw = []
        for j in neighbors:
            # select the appropriate method
            if method == SocioWeight.SIMILARITY:
                raw.append(1 / (1 + abs(normalized_index[i] - normalized_index[j])))
            elif method == SocioWeight.GRADIENT:
                raw.append(abs(normalized_index[i] - normalized_index[j]))
            elif method == SocioWeight.PRODUCT:
                raw.append(normalized_index[i] * normalized_index[j])

        # row standardize
        total = sum(raw)
        if total > 0:
            new_weights[i] = [w / total for w in raw]
        else:
            # isolated node or all-zero weights (a gradient with identical neighbors)
            new_weights[i] = [0.0 for _ in raw]

    logger.info("Socioeconomic SWM created with %s units", len(new_weights))

    return WObject(base_w.neighbors, new_weights)