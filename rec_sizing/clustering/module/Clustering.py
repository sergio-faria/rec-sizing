import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle

from datetime import datetime
from sklearn_extra.cluster import KMedoids

from rec_sizing.custom_types.clustering_types import (
    BackpackKMedoids,
    OutputsKMedoids
)


def clustering_kmedoids(inputs: BackpackKMedoids) -> OutputsKMedoids:
    """
    Implements sklearn_extra's K-Medoids clustering algorithm to partition the given data for a given meter into
    user-defined number of clusters.
    Data must be provided in a fixed, yet configurable time step, in multiples of 1 day, and must include 4 series of
    data per day: generation PV factor, consumption in kWh and buying and selling opportunity costs in €/kWh

    :param inputs: dictionary with the data to be clustered, the data's time step, the number of days included
    and the desired number of resulting clusters (i.e., representative days)

    :return: dictionary with the medoids (representative days) separated by data serie, the medoid label attributed to
    each day, an inertia parameter (representing an intracluster distance) and the number of days per clusters
    """
    nr_days = inputs['nr_days']
    delta_t = inputs['delta_t']
    # Number of meters defined
    meter_ids = inputs['timeseries_data'].keys()
    nr_meters = len(meter_ids)
    # Number of data points in a day for a single var (e_g, e_c, l_buy or l_sell; l_grid not included)
    nr_daily_points_per_var = int(24 * nr_meters / delta_t)
    # Number of total data points for a single var (e_g, e_c, l_buy or l_sell; l_grid not included)
    nr_points_per_var = int(nr_days * 24 * nr_meters / delta_t)
    # Number of data points in a day for a single var and single meter (e_g, e_c, l_buy, l_sell and l_grid)
    nr_daily_delta_t = int(24 / delta_t)

    # Create an auxiliary dataframe version of the inputs
    inputs_df = None
    for meter_id in meter_ids:
        if inputs_df is not None:
            meter_df = pd.DataFrame(inputs['timeseries_data'][meter_id])
            meter_df['meter_id'] = meter_id
            meter_df['date'] = 0
            inputs_df = pd.concat([inputs_df, meter_df], axis=0)
        else:
            inputs_df = pd.DataFrame(inputs['timeseries_data'][meter_id])
            inputs_df['meter_id'] = meter_id
            inputs_df['date'] = 0
    inputs_df.reset_index(inplace=True, drop=True)

    inputs_df['hours'] = list(range(nr_daily_delta_t * nr_days)) * nr_meters
    inputs_df['date'] = inputs_df['hours'] // 24

    # Check that the number of timeseries data points provided matches the number of days times the step in hours
    assert len(inputs_df) == nr_points_per_var, \
        f'The number of timeseries data points ({len(inputs_df)}) provided ' \
        f'does not match nr_days * 24 / delta_t = {nr_points_per_var}'

    # Create auxiliry array of the grid tariffs' list
    l_grid_array = np.array(inputs['l_grid'])

    # Re-organize data into lists of lists, where each list represents a different type of data
    # and each sublist has the extent of one day * nr_meters
    # Results in an array with nr_days arrays, each with length = nr_daily_delta_t * nr_meters, except for
    # l_grid_matrix with length = nr_daily_delta_t, since it is meter-agnostic
    e_g_ready = np.array([inputs_df.loc[inputs_df['date'] == date, 'e_g_factor'].values for date in range(nr_days)])
    e_c_matrix = np.array([inputs_df.loc[inputs_df['date'] == date, 'e_c'].values for date in range(nr_days)])
    l_buy_matrix = np.array([inputs_df.loc[inputs_df['date'] == date, 'l_buy'].values for date in range(nr_days)])
    l_sell_matrix = np.array([inputs_df.loc[inputs_df['date'] == date, 'l_sell'].values for date in range(nr_days)])

    l_grid_matrix = l_grid_array.reshape(nr_days, nr_daily_delta_t)

    # Normalize data of load and prices by scaling
    # each normalized value is now given by xnew = (x - xmin)/(xmax - x min)
    def normalize_matrix(matrix: np.ndarray[np.ndarray[float]]) -> np.ndarray[np.ndarray[float]]:
        matrix_max = np.max(matrix)
        matrix_min = np.min(matrix)
        check_div_zero = matrix_max - matrix_min > 0
        return (matrix - matrix_min) / (matrix_max - matrix_min) if check_div_zero else (matrix - matrix_min)

    e_c_ready = normalize_matrix(e_c_matrix)
    l_buy_ready = normalize_matrix(l_buy_matrix)
    l_sell_ready = normalize_matrix(l_sell_matrix)
    l_grid_ready = normalize_matrix(l_grid_matrix)

    # Join all matrixes
    # Results in an array with nr_days arrays, each with length = nr_daily_delta_t * nr_meters * 4 + nr_daily_delta_t,
    # since each day is characterized by the e_g, e_c, l_buy and l_sell (4 vars) of each meter
    # and the meter-agnostic l_grid tariffs
    all_ready = np.concatenate((e_g_ready, e_c_ready, l_buy_ready, l_sell_ready, l_grid_ready), axis=1)

    # Desired number of clusters (i.e., the number of representative days)
    nr_clusters = inputs['nr_representative_days']

    # Apply k-medoids
    kmedoids = KMedoids(n_clusters=nr_clusters)
    kmedoids.fit(all_ready)
    day_cluster_labels = kmedoids.fit_predict(all_ready)  # returns the label of the cluster to which each day belongs
    day_cluster_labels = day_cluster_labels.astype(str)
    # - get matrix of the centroids of the clustering method of dimension (nr_clusters, #variables)
    rep_days_matrix = kmedoids.cluster_centers_
    total_distance_calculation = round(kmedoids.inertia_, 3)

    # Individualize each variable at the representative days matrix
    # Note that each representative day in the rep_days_matrix, i.e., each sublist has
    # length = nr_daily_delta_t * nr_meters * 4 + nr_daily_delta_t; the first nr_daily_delta_t * nr_meters are the
    # e_g timeseries and so on
    up_limit_e_g = nr_daily_points_per_var
    rep_days_e_g_final = rep_days_matrix[:, :up_limit_e_g]

    dn_limit_e_c = up_limit_e_g
    up_limit_e_c = nr_daily_points_per_var * 2
    rep_days_e_c_normalized = rep_days_matrix[:, dn_limit_e_c:up_limit_e_c]

    dn_limit_l_buy = up_limit_e_c
    up_limit_l_buy = nr_daily_points_per_var * 3
    rep_days_l_buy_normalized = rep_days_matrix[:, dn_limit_l_buy:up_limit_l_buy]

    dn_limit_l_sell = up_limit_l_buy
    up_limit_l_sell = nr_daily_points_per_var * 4
    rep_days_l_sell_normalized = rep_days_matrix[:, dn_limit_l_sell:up_limit_l_sell]

    dn_limit_l_grid = up_limit_l_sell
    up_limit_l_grid = dn_limit_l_grid + nr_daily_delta_t
    rep_days_l_grid_normalized = rep_days_matrix[:, dn_limit_l_grid:up_limit_l_grid]

    # Revert normalization (scaling)
    def denormalize_matrix(original_matrix: np.ndarray[np.ndarray[float]],
                           normalized_matrix: np.ndarray[np.ndarray[float]]) -> np.ndarray[np.ndarray[float]]:
        matrix_max = np.max(original_matrix)
        matrix_min = np.min(original_matrix)
        return normalized_matrix * (matrix_max - matrix_min) + matrix_min

    rep_days_e_c_final = denormalize_matrix(e_c_matrix, rep_days_e_c_normalized)
    rep_days_l_buy_final = denormalize_matrix(l_buy_matrix, rep_days_l_buy_normalized)
    rep_days_l_sell_final = denormalize_matrix(l_sell_matrix, rep_days_l_sell_normalized)
    rep_days_l_grid_final = denormalize_matrix(l_grid_matrix, rep_days_l_grid_normalized)

    # Find the number of days per cluster
    unique_cluster_labels, cluster_counts = np.unique(day_cluster_labels, return_counts=True)

    # Fill and return the outputs
    representative_e_g_factor = {
        meter_id: {
            cluster_label:
                list(rep_days_e_g_final[idx_cluster][
                     int(nr_daily_delta_t * idx_meter):int(nr_daily_delta_t*(idx_meter+1))].round(3))
            for idx_cluster, cluster_label in enumerate(unique_cluster_labels)
        }
        for idx_meter, meter_id in enumerate(meter_ids)
    }

    representative_e_c = {
        meter_id: {
            cluster_label:
                list(rep_days_e_c_final[idx_cluster][
                     int(nr_daily_delta_t*idx_meter):int(nr_daily_delta_t*(idx_meter+1))].round(3))
            for idx_cluster, cluster_label in enumerate(unique_cluster_labels)
        }
        for idx_meter, meter_id in enumerate(meter_ids)
    }

    representative_l_buy = {
        meter_id: {
            cluster_label:
                list(rep_days_l_buy_final[idx_cluster][
                     int(nr_daily_delta_t*idx_meter):int(nr_daily_delta_t*(idx_meter+1))].round(6))
            for idx_cluster, cluster_label in enumerate(unique_cluster_labels)
        }
        for idx_meter, meter_id in enumerate(meter_ids)
    }

    representative_l_sell = {
        meter_id: {
            cluster_label:
                list(rep_days_l_sell_final[idx_cluster][
                     int(nr_daily_delta_t*idx_meter):int(nr_daily_delta_t*(idx_meter+1))].round(6))
            for idx_cluster, cluster_label in enumerate(unique_cluster_labels)
        }
        for idx_meter, meter_id in enumerate(meter_ids)
    }

    representative_l_grid = {
        cluster_label:
            list(rep_days_l_grid_final[idx_cluster].round(6))
        for idx_cluster, cluster_label in enumerate(unique_cluster_labels)
    }

    cluster_nr_days = {
        cluster_label: cluster_count
        for cluster_label, cluster_count in zip(unique_cluster_labels, cluster_counts)
    }

    outputs = {
        'inertia': total_distance_calculation,
        'cluster_labels': list(day_cluster_labels),
        'representative_e_g_factor': representative_e_g_factor,
        'representative_e_c': representative_e_c,
        'representative_l_buy': representative_l_buy,
        'representative_l_sell': representative_l_sell,
        'representative_l_grid': representative_l_grid,
        'cluster_nr_days': cluster_nr_days
    }

    return outputs
