import logging

from libpysal.weights import Rook, Queen

logger = logging.getLogger(__name__)

def create_rook_swm(geodf):
    logger.info("Creating Rook Matrix")
    w_rook = Rook.from_dataframe(geodf, use_index=True)
    logger.info(w_rook.neighbors[0])

    return w_rook

def create_queen_swm(geodf):
    logger.info("Creating Queen Matrix")
    w_queen = Queen.from_dataframe(geodf, use_index=True)
    logger.info(w_queen.neighbors[0])

    return w_queen

