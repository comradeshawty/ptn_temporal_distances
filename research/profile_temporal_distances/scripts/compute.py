from __future__ import print_function

import os
import pickle

import networkx
import pandas

from gtfspy.routing.connection_scan_profile import ConnectionScanProfiler
from gtfspy.routing.models import Connection
from routing.node_profile import NodeProfile
from routing.node_profile_analyzer import NodeProfileAnalyzer

from settings import HELSINKI_DATA_BASEDIR, RESULTS_DIRECTORY, ROUTING_START_TIME_DEP, ROUTING_END_TIME_DEP, \
    ANALYSIS_START_TIME_DEP, HELSINKI_NODES_FNAME, ANALYSIS_END_TIME_DEP


NPA = NodeProfileAnalyzer  # just a shorter alias for the lines below
profile_summary_methods = [
    NPA.min_trip_duration, NPA.max_trip_duration, NPA.mean_trip_duration, NPA.median_trip_duration,
    NPA.min_temporal_distance, NPA.max_temporal_distance, NPA.mean_temporal_distance, NPA.mean_temporal_distance,
    NPA.n_pareto_optimal_trips
]
NPA = None

profile_observable_names = [
    "min_trip_duration", "max_trip_duration", "mean_trip_duration", "median_trip_duration",
    "min_temporal_distance", "max_temporal_distance", "mean_temporal_distance", "median_temporal_distance",
    "n_trips"
]


def get_profile_data(target_stop_I=115, recompute=False):
    node_profiles_fname = os.path.join(RESULTS_DIRECTORY, "node_profile_" + str(target_stop_I) + ".pickle")
    if not recompute and os.path.exists(node_profiles_fname):
        print("Loading precomputed data")
        profiles = pickle.load(open(node_profiles_fname, 'rb'))
        print("Loaded precomputed data")
    else:
        print("Recomputing profiles")
        profiles = _compute_profile_data(target_stop_I)
        pickle.dump(profiles, open(node_profiles_fname, 'wb'), -1)
        print("Recomputing profiles")
    return profiles


def get_node_profile_statistics(target_stop_I, recompute=False, recompute_profiles=False):
    profile_statistics_fname = os.path.join(RESULTS_DIRECTORY, "node_profile_statistics_" +
                                            str(target_stop_I) + ".pickle")
    if recompute_profiles:
        recompute = True
    if not recompute and os.path.exists(profile_statistics_fname):
        print("Loading precomputed statistics")
        observable_name_to_data = pickle.load(open(profile_statistics_fname, 'rb'))
        print("Loaded precomputed statistics")
    else:
        print("Recomputing statistics")
        observable_name_to_data = _compute_node_profile_statistics(target_stop_I, recompute_profiles)
        pickle.dump(observable_name_to_data, open(profile_statistics_fname, 'wb'), -1)
        print("Recomputed statistics")
    return observable_name_to_data


def _compute_profile_data(target_stop_I=115):
    events = pandas.read_csv(HELSINKI_DATA_BASEDIR + "main.day.temporal_network.csv")
    events = events[events["dep_time_ut"] >= ROUTING_START_TIME_DEP]
    time_filtered_events = events[events["dep_time_ut"] <= ROUTING_END_TIME_DEP]
    time_filtered_events.sort_values("dep_time_ut", ascending=False, inplace=True)

    connections = [
        Connection(int(e.from_stop_I), int(e.to_stop_I), int(e.dep_time_ut), int(e.arr_time_ut), int(e.trip_I))
        for e in time_filtered_events.itertuples()
    ]

    transfers = pandas.read_csv(HELSINKI_DATA_BASEDIR + "main.day.transfers.csv")
    filtered_transfers = transfers[transfers["d_walk"] <= 500]
    net = networkx.Graph()
    for row in filtered_transfers.itertuples():
        net.add_edge(int(row.from_stop_I), int(row.to_stop_I), {"d_walk": row.d_walk})

    csp = ConnectionScanProfiler(connections, target_stop=target_stop_I, walk_network=net, walk_speed=1.5)
    print("CSA Profiler running...")
    csp.run()
    print("CSA profiler finished")

    profiles = {"target_stop_I": target_stop_I, "profiles": dict(csp.stop_profiles)}
    return profiles


def _compute_node_profile_statistics(target_stop_I, recompute_profiles=False):
    profile_data = get_profile_data(target_stop_I, recompute=recompute_profiles)['profiles']
    profile_summary_data = [[] for _ in range(len(profile_observable_names))]

    observable_name_to_method = dict(zip(profile_observable_names, profile_summary_methods))
    observable_name_to_data = dict(zip(profile_observable_names, profile_summary_data))

    nodes = pandas.read_csv(HELSINKI_NODES_FNAME)
    for stop_I in nodes['stop_I'].values:
        try:
            profile = profile_data[stop_I]
        except KeyError:
            profile = NodeProfile()
        profile_analyzer = NodeProfileAnalyzer(profile, ANALYSIS_START_TIME_DEP, ANALYSIS_END_TIME_DEP)
        for observable_name in profile_observable_names:
            method = observable_name_to_method[observable_name]
            observable_value = method(profile_analyzer)
            observable_name_to_data[observable_name].append(observable_value)
    return observable_name_to_data