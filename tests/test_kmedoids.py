import os
import pandas as pd
import pickle

from rec_sizing.clustering.module.Clustering import clustering_kmedoids
from rec_sizing.clustering.structures.I_O_clustering import (
	CLUSTERING_INPUTS,
	CLUSTERING_OUTPUTS
)


def test_clustering_kmedoids():
	# Assert the generation of the expected kmedoids
	# run clustering
	outputs = clustering_kmedoids(CLUSTERING_INPUTS)
	assert outputs == CLUSTERING_OUTPUTS


if __name__ == '__main__':
	test_clustering_kmedoids()
