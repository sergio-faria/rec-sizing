INPUTS_POOL_EVS = {
	'nr_days': 1/8,
	'l_grid': [0.01, 0.01, 0.01],
	'delta_t': 1.0,
	'storage_ratio': 1.0,
	'strict_pos_coeffs': True,
	'total_share_coeffs': True,
	'meters': {
		'Meter#1': {
			'l_buy': [2.0, 2.0, 2.0],
			'l_sell': [0.0, 0.0, 0.9],
			'l_cont': 0.1,
			'l_gic': 0.1,
			'l_bic': 0.1,
			'e_c': [0.0, 0.5, 0.0],
			'p_meter_max': 10,
			'p_gn_init': 1.0,
			'e_g_factor': [0.5, 0.0, 0.0],
			'p_gn_min': 0.0,
			'p_gn_max': 0.0,
			'e_bn_init': 0.0,
			'e_bn_min': 0.0,
			'e_bn_max': 1.0,
			'soc_min': 0.0,
			'eff_bc': 1.0,
			'eff_bd': 1.0,
			'soc_max': 100.0,
			'deg_cost': 0.0,
			'btm_evs': {
				'EV#1': {
					'trip_ev': [0, 0.3, 0],
					'min_energy_storage_ev': .1,
					'battery_capacity_ev': 1,
					'eff_bc_ev': 0.99,
					'eff_bd_ev': 0.99,
					'init_e_ev': 0.9,
					'pmax_c_ev': 0.1,
					'pmax_d_ev': 0.1,
					'bin_ev': [1, 0, 1]
						},
					'EV#2': {
					'trip_ev': [0, 0.3, 0],
					'min_energy_storage_ev': .1,
					'battery_capacity_ev': 1,
					'eff_bc_ev': 0.99,
					'eff_bd_ev': 0.99,
					'init_e_ev': 0.9,
					'pmax_c_ev': 0.1,
					'pmax_d_ev': 0.1,
					'bin_ev': [1, 0, 1]
						}
					}
		},
		'Meter#2': {
			'l_buy': [2.0, 2.0, 2.0],
			'l_sell': [0.0, 0.0, 0.0],
			'l_cont': 0.1,
			'l_gic': 0.0,
			'l_bic': 0.1,
			'e_c': [0.1, 0.1, 0.1],
			'p_meter_max': 10,
			'p_gn_init': 0.0,
			'e_g_factor': [0.1, 0.1, 0.1],
			'p_gn_min': 0.0,
			'p_gn_max': 1.0,
			'e_bn_init': 0.0,
			'e_bn_min': 0.0,
			'e_bn_max': 0.0,
			'soc_min': 0.0,
			'eff_bc': 1.0,
			'eff_bd': 1.0,
			'soc_max': 100.0,
			'deg_cost': 0.0,
			'btm_evs': {
				'EV#1': {
					'trip_ev': [0, 0.3, 0],
					'min_energy_storage_ev': 0,
					'battery_capacity_ev': 1,
					'eff_bc_ev': 0.99,
					'eff_bd_ev': 0.99,
					'init_e_ev': 0.9,
					'pmax_c_ev': 0.1,
					'pmax_d_ev': 0.1,
					'bin_ev': [1, 0, 1]
						},
				'EV#2': {
					'trip_ev': [0, 0.3, 0],
					'min_energy_storage_ev': 0,
					'battery_capacity_ev': 1,
					'eff_bc_ev': 0.99,
					'eff_bd_ev': 0.99,
					'init_e_ev': 0.25,
					'pmax_c_ev': 0.1,
					'pmax_d_ev': 0.1,
					'bin_ev': [1, 0, 1]
						}
					}
		}
	}
}

OUTPUTS_POOL_EVS = {
    "obj_value": -0.473,
    "milp_status": "Optimal",
    'nr_dates': 0.125,
    'w_clustering': [1, 1, 1],
    "p_cont": {
        "Meter#1": 0.396,
        "Meter#2": 0.1465299
    },
    "p_gn_new": {
        "Meter#1": 0.0,
        "Meter#2": 1.0
    },
    "p_gn_total": {
        "Meter#1": 1.0,
        "Meter#2": 1.0
    },
    "e_bn_new": {
        "Meter#1": 0.698,
        "Meter#2": 0.0
    },
    "e_bn_total": {
        "Meter#1": 0.698,
        "Meter#2": 0.0
    },
    "e_cmet": {
        "Meter#1": [
            0.0,
            0.0,
            -0.396
        ],
        "Meter#2": [
            0.0,
            0.0,
            -0.1465299
        ]
    },
    "e_g": {
        "Meter#1": [
            0.5,
            0.0,
            0.0
        ],
        "Meter#2": [
            0.1,
            0.1,
            0.1
        ]
    },
    "e_bc": {
        "Meter#1": [
            0.698,
            0.0,
            0.0
        ],
        "Meter#2": [
            0.0,
            0.0,
            0.0
        ]
    },
    "e_bd": {
        "Meter#1": [
            0.0,
            0.5,
            0.198
        ],
        "Meter#2": [
            0.0,
            0.0,
            0.0
        ]
    },
    "e_sup": {
        "Meter#1": [
            0.0,
            0.0,
            0.0
        ],
        "Meter#2": [
            0.0,
            0.0,
            0.0
        ]
    },
    "e_sur": {
        "Meter#1": [
            0.0,
            0.0,
            0.5425299
        ],
        "Meter#2": [
            0.0,
            0.0,
            0.0
        ]
    },
    "e_pur_pool": {
        "Meter#1": [
            0.0,
            0.0,
            0.1465299
        ],
        "Meter#2": [
            0.0,
            0.0,
            0.0
        ]
    },
    "e_sale_pool": {
        "Meter#1": [
            0.0,
            0.0,
            0.0
        ],
        "Meter#2": [
            0.0,
            0.0,
            0.1465299
        ]
    },
    "e_slc_pool": {
        "Meter#1": [
            0.0,
            0.0,
            0.0
        ],
        "Meter#2": [
            0.0,
            0.0,
            0.0
        ]
    },
    "e_bat": {
        "Meter#1": [
            0.698,
            0.198,
            0.0
        ],
        "Meter#2": [
            0.0,
            0.0,
            0.0
        ]
    },
    "delta_sup": {
        "Meter#1": [
            0.0,
            0.0,
            0.0
        ],
        "Meter#2": [
            0.0,
            0.0,
            0.0
        ]
    },
    "e_consumed": {
        "Meter#1": [
            0.0,
            0.0,
            0.0
        ],
        "Meter#2": [
            0.0,
            0.0,
            0.0
        ]
    },
    "e_alc": {
        "Meter#1": [
            0.0,
            0.0,
            0.1465299
        ],
        "Meter#2": [
            0.0,
            0.0,
            0.0
        ]
    },
    "delta_slc": {
        "Meter#1": [
            1.0,
            0.0,
            1.0
        ],
        "Meter#2": [
            0.0,
            0.0,
            0.0
        ]
    },
    "ev_stored": {
        "Meter#1": {
            "EV#1": [
                0.8,
                0.5,
                0.4
            ],
            "EV#2": [
                0.8,
                0.5,
                0.4
            ]
        },
        "Meter#2": {
            "EV#1": [
                0.8,
                0.5,
                0.4
            ],
            "EV#2": [
                0.34801,
                0.04801,
                0.0
            ]
        }
    },
    "p_ev_charge": {
        "Meter#1": {
            "EV#1": [
                0.0,
                0.0,
                0.0
            ],
            "EV#2": [
                0.0,
                0.0,
                0.0
            ]
        },
        "Meter#2": {
            "EV#1": [
                0.0,
                0.0,
                0.0
            ],
            "EV#2": [
                0.099,
                0.0,
                0.0
            ]
        }
    },
    "p_ev_discharge": {
        "Meter#1": {
            "EV#1": [
                0.099,
                0.0,
                0.099
            ],
            "EV#2": [
                0.099,
                0.0,
                0.099
            ]
        },
        "Meter#2": {
            "EV#1": [
                0.099,
                0.0,
                0.099
            ],
            "EV#2": [
                0.0,
                0.0,
                0.0475299
            ]
        }
    },
    "delta_coeff": {
        "Meter#1": [
            0.0,
            0.0,
            0.0
        ],
        "Meter#2": [
            0.0,
            0.0,
            0.0
        ]
    },
    "delta_rec_balance": [
        0.0,
        0.0,
        1.0
    ],
    "delta_meter_balance": {
        "Meter#1": [
            0.0,
            0.0,
            1.0
        ],
        "Meter#2": [
            1.0,
            0.0,
            1.0
        ]
    },
    "c_ind2pool": {
        "Meter#1": -0.475,
        "Meter#2": 0.002
    },
    "dual_prices": [
        0.8698,
        0.8875,
        0.9
    ]
}
