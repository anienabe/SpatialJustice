import logging

from libpysal.weights import Rook, Queen

logger = logging.getLogger(__name__)

def create_rook_swm(geodf):
    logger.info("Creating Rook Matrix")
    w_rook = Rook.from_dataframe(geodf, use_index=True)
    first_id = list(w_rook.neighbors.keys())[0]
    logger.info(w_rook.neighbors[first_id])

    return w_rook

def create_queen_swm(geodf):
    logger.info("Creating Queen Matrix")
    w_queen = Queen.from_dataframe(geodf, use_index=True)
    first_id = list(w_queen.neighbors.keys())[0]
    logger.info(w_queen.neighbors[first_id])

    return w_queen

