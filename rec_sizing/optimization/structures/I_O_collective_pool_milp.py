INPUTS_NO_INSTALL_POOL = {
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
			'e_g_factor': [0.9, 0.0, 0.0],
			'p_gn_min': 0.0,
			'p_gn_max': 0.0,
			'e_bn_init': 1.0,
			'e_bn_min': 0.0,
			'e_bn_max': 0.0,
			'soc_min': 0.0,
			'eff_bc': 1.0,
			'eff_bd': 1.0,
			'soc_max': 100.0
		},
		'Meter#2': {
			'l_buy': [2.0, 2.0, 2.0],
			'l_sell': [0.0, 0.0, 0.0],
			'l_cont': 0.1,
			'l_gic': 0.1,
			'l_bic': 0.1,
			'e_c': [0.1, 0.1, 0.1],
			'p_meter_max': 10,
			'p_gn_init': 0.0,
			'e_g_factor': [0.0, 0.0, 0.0],
			'p_gn_min': 0.0,
			'p_gn_max': 0.0,
			'e_bn_init': 0.0,
			'e_bn_min': 0.0,
			'e_bn_max': 0.0,
			'soc_min': 0.0,
			'eff_bc': 1.0,
			'eff_bd': 1.0,
			'soc_max': 100.0
		}
	}
}

OUTPUTS_NO_INSTALL_POOL = {
    "obj_value": -0.083,
    "milp_status": "Optimal",
    "p_cont": {
        "Meter#1": 0.2,
        "Meter#2": 0.1
    },
    "p_gn_new": {
        "Meter#1": 0.0,
        "Meter#2": 0.0
    },
    "p_gn_total": {
        "Meter#1": 1.0,
        "Meter#2": 0.0
    },
    "e_bn_new": {
        "Meter#1": 0.0,
        "Meter#2": 0.0
    },
    "e_bn_total": {
        "Meter#1": 1.0,
        "Meter#2": 0.0
    },
    "e_cmet": {
        "Meter#1": [-0.1, -0.1, -0.2],
        "Meter#2": [0.1, 0.1, 0.1]
    },
    "e_g": {
        "Meter#1": [0.9, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "e_bc": {
        "Meter#1": [0.8, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "e_bd": {
        "Meter#1": [0.0, 0.6, 0.2],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "e_sup": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "e_sur": {
        "Meter#1": [0.0, 0.0, 0.1],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "e_pur_pool": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.1, 0.1, 0.1]
    },
    "e_sale_pool": {
        "Meter#1": [0.1, 0.1, 0.1],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "e_slc_pool": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.1, 0.1, 0.1]
    },
    "delta_bc": {
        "Meter#1": [1.0, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "e_bat": {
        "Meter#1": [0.8, 0.2, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "delta_sup": {
        "Meter#1": [1.0, 1.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "e_consumed": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.1, 0.1, 0.1]
    },
    "e_alc": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.1, 0.1, 0.1]
    },
    "delta_slc": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 1.0]
    },
    "delta_cmet": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "delta_alc": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "delta_coeff": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "delta_rec_balance": [0.0, 1.0, 1.0],
    "delta_meter_balance": {
        "Meter#1": [1.0, 1.0, 1.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "c_ind2pool": {
        "Meter#1": -0.088,
        "Meter#2": 0.004
    },
    "dual_prices": [0.8875, 0.0, 0.9]
}

INPUTS_INSTALL_POOL = {
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
			'soc_max': 100.0
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
			'soc_max': 100.0
		}
	}
}

OUTPUTS_INSTALL_POOL = {
    "obj_value": 0.006,
    "milp_status": "Optimal",
    "p_cont": {
        "Meter#1": 0.0,
        "Meter#2": 0.0
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
        "Meter#1": 0.5,
        "Meter#2": 0.0
    },
    "e_bn_total": {
        "Meter#1": 0.5,
        "Meter#2": 0.0
    },
    "e_cmet": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "e_g": {
        "Meter#1": [0.5, 0.0, 0.0],
        "Meter#2": [0.1, 0.1, 0.1]
    },
    "e_bc": {
        "Meter#1": [0.5, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "e_bd": {
        "Meter#1": [0.0, 0.5, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "e_sup": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "e_sur": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "e_pur_pool": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "e_sale_pool": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "e_slc_pool": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "delta_bc": {
        "Meter#1": [1.0, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "e_bat": {
        "Meter#1": [0.5, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "delta_sup": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "e_consumed": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "e_alc": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "delta_slc": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "delta_cmet": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "delta_alc": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "delta_coeff": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "delta_rec_balance": [0.0, 0.0, 0.0],
    "delta_meter_balance": {
        "Meter#1": [0.0, 0.0, 0.0],
        "Meter#2": [0.0, 0.0, 0.0]
    },
    "c_ind2pool": {
        "Meter#1": 0.006,
        "Meter#2": 0.0
    },
    "dual_prices": [0.0, 0.0, 0.9]
}
