"""generate plots for REC optimization and post-processing"""
"""only able to generate plots for post-processing results"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def plot_results_optimization(outputs, inputs, outputs_dir):
    set_meters = list(inputs['meters'])
    #VARIAVEIS PARA EIXOS
    time = np.arange(0, inputs['nr_days']*24*inputs['delta_t']+1, inputs['delta_t'])
    bar_width = 0.3
    color = 'tab:red'
    '''Plot 1 - ENERGIA, CARGA E DESCARGA DA BATERIA DA INSTALAÇÃO N '''
    for name in set_meters:
        b_energy = outputs['e_bat'][name].copy()    # battery energy stored in n [kWh]
        init_e_bat = inputs['meters'][name]['soc_min'] / 100 * outputs['p_gn_total'][name]
        b_energy.insert(0, init_e_bat)
        p_load = inputs['meters'][name]['e_c'].copy()   # meter load profile [kWh]
        p_load.insert(len(inputs['meters'][name]['e_c']), np.nan)
        p_gen = outputs['e_g'][name].copy()   # behind-the-meter generation at meter n [kWh]
        p_gen.insert(len(p_gen), np.nan)
        p_grid_in = outputs['e_sup'][name].copy()   # energy supplied to n from its retailer [kWh]
        p_grid_in.insert(len(p_grid_in), np.nan)
        p_grid_out = outputs['e_sur'][name].copy()     # energy surplus sold by n to its retailer [kWh]
        p_grid_out.insert(len(p_grid_out), np.nan)
        buy_price = inputs['meters'][name]['l_buy'].copy()
        buy_price.insert(len(buy_price), np.nan)
        sell_tariff = inputs['meters'][name]['l_sell'].copy()
        sell_tariff.insert(len(sell_tariff), np.nan)
        sold_position = outputs['sold_position'][name].copy()
        sold_position.insert(len(sold_position), np.nan)
        ShadowPrice = outputs['dual_prices'].copy()
        ShadowPrice.insert(len(ShadowPrice), np.nan)

        fig1, ax1 = plt.subplots(figsize=(12, 8))
        plt.yticks(fontsize=8)
        plt.xticks(time, fontsize=6)
        plt.ylabel('Energy (kWh)', fontsize=10)
        plt.xlabel('Hours', fontsize=10)
        plt.title(name)
        plt.plot(time, b_energy, 'b-', label='Battery')
        plt.plot(time + 0.5, p_load, 'k^', label='Load', markersize=6)
        plt.bar(time + 0.5, p_gen, width=bar_width, color=(1.0, 0.8, 0.0), alpha=0.7, align='center', label='PV')
        plt.plot(time + 0.5, p_grid_in, 'r.-', label='Supply', linewidth=0.8, markersize=7)
        plt.plot(time + 0.5, p_grid_out, 'g.-', label='Surplus', linewidth=0.8, markersize=5)
        plt.plot(time + 0.5, sold_position, 'y.-', label='sold_position', linewidth=0.8, markersize=5)
        plt.grid(axis='both')
        y_margin = abs(max(ax1.get_ylim())) * 0.05
        ax1.set_ylim(min(ax1.get_ylim()) - y_margin, None)
        plt.legend(loc="upper center", bbox_to_anchor=(0.785, 1.078), ncol=3, fontsize=6)
        ax2 = ax1.twinx()
        ax2.set_ylabel('Buy/Sell prices (€/kWh)', fontsize=8, color=color)
        ax2.plot(time + 0.5, buy_price, '-', color=(0.8, 0.0, 0.0), linewidth=2, alpha=0.4, label="buy price")
        ax2.plot(time + 0.5, sell_tariff, '-', color=(0.0, 0.3, 0.0), linewidth=2, alpha=0.4, label="sell price")
        if len(ShadowPrice)>1:
            ax2.plot(time + 0.5, ShadowPrice, 'b--', linewidth=0.8, alpha=0.6, label="ShadowPrice")
        ax2.tick_params(axis='y', labelcolor=color)
        plt.yticks(fontsize=8)
        y_margin2 = abs(max(ax2.get_ylim())) * 0.05
        plt.ylim(ymin=(0 - y_margin2), ymax=max(ax2.get_ylim())+y_margin2)
        plt.legend(loc="upper right", bbox_to_anchor=(1.006, 1.078), fontsize=6)
        plt.savefig(outputs_dir + name, bbox_inches='tight')

def plot_results_installationCosts(outputs, outputs_dir):
    ''' #Custos por instalação '''
    fig2, ax1 = plt.subplots(figsize=(12, 8))
    plt.ylabel('Cost (€)', fontsize=12)
    plt.xlabel('Installation_id', fontsize=10)
    plt.title('REC Costs: installation')
    # plt.ylim([-4, 12])
    bar_width = 0.1
    installations_cost = outputs['c_ind2pool']
    len_CPE = len(installations_cost.keys())

    r1 = np.arange(len_CPE)
    r2 = [x + bar_width for x in r1]
    r3 = [x + bar_width for x in r2]
    r4 = [x + bar_width for x in r3]
    r5 = [x + bar_width for x in r4]
    r6 = [x + bar_width for x in r5]
    r7 = [x + bar_width for x in r6]

    plt.yticks(fontsize=8)
    plt.xticks([r + (7/2*bar_width) for r in range(len_CPE)], list(installations_cost.keys()), fontsize=6)

    retailer_exchanges_cost = outputs['retailer_exchanges_cost']
    data = pd.DataFrame.from_dict(retailer_exchanges_cost.values())
    data.index = retailer_exchanges_cost.keys()
    plt.bar(r1, data[0], width=bar_width, label='retailer_exchanges_cost')

    sc_tariff_cost = outputs['sc_tariff_cost']
    data = pd.DataFrame.from_dict(sc_tariff_cost.values())
    data.index = sc_tariff_cost.keys()
    plt.bar(r2, data[0], width=bar_width, label='sc_tariff_cost')

    contracted_power_cost = outputs['contractedpower_cost']
    data = pd.DataFrame.from_dict(contracted_power_cost.values())
    data.index = contracted_power_cost.keys()
    plt.bar(r3, data[0], width=bar_width, label='contracted_power_cost')

    batteries_investments_cost = outputs['batteries_investments_cost']
    data = pd.DataFrame.from_dict(batteries_investments_cost.values())
    data.index = batteries_investments_cost.keys()
    plt.bar(r4, data[0], width=bar_width, label='batteries_investments_cost')

    PV_investments_cost = outputs['PV_investments_cost']
    data = pd.DataFrame.from_dict(PV_investments_cost.values())
    data.index = PV_investments_cost.keys()
    plt.bar(r5, data[0], width=bar_width, label='PV_investments_cost')

    data = pd.DataFrame.from_dict(installations_cost.values())
    data.index = installations_cost.keys()
    plt.bar(r6, data[0], width=bar_width, label='installations_cost')

    installations_cost_compensations = outputs['installation_cost_compensations']
    data = pd.DataFrame.from_dict(installations_cost_compensations.values())
    data.index = installations_cost_compensations.keys()
    plt.bar(r7, data[0], width=bar_width, label='installations_cost_compensations')

    plt.legend(loc="upper right", fontsize=12)
    ax1.set_axisbelow(True)
    ax1.yaxis.grid(color='gray', linestyle='-', alpha=0.5)
    plt.savefig(outputs_dir + 'REC_costs_installation', bbox_inches='tight')

def plot_results_membersCosts(outputs, outputs_dir):
    ''' #Custos por membro '''
    fig3, ax1 = plt.subplots(figsize=(12, 8))
    plt.yticks(fontsize=8)
    plt.xticks(fontsize=6)
    plt.ylabel('Cost (€)', fontsize=10)
    plt.xlabel('member_id', fontsize=10)
    # plt.ylim([0, 1])
    plt.title('REC Costs: members')

    width_bar = 0.4
    distance_label = 0.01 * max(list(outputs['member_cost'].values())+list(outputs['member_cost_compensations'].values()))
    def addlabels_left(x, y):
        for i in range(len(x)):
            if y.iloc[i] < 0:
                plt.text(i - width_bar/2, y.iloc[i] - distance_label, round(y.iloc[i], 3), ha='center')
            else:
                plt.text(i - width_bar/2, y.iloc[i] + distance_label, round(y.iloc[i], 3), ha='center')
    def addlabels_right(x, y):
        for i in range(len(x)):
            if y.iloc[i] < 0:
                plt.text(i + width_bar/2, y.iloc[i] - distance_label, round(y.iloc[i], 3), ha='center')
            else:
                plt.text(i + width_bar/2, y.iloc[i] + distance_label, round(y.iloc[i], 3), ha='center')

    prosumer_cost = outputs['member_cost']
    data = pd.DataFrame.from_dict(prosumer_cost.values())
    data.index = prosumer_cost.keys()
    plt.bar(list(prosumer_cost.keys()), data[0], align='edge', width=-width_bar, label='member cost')
    addlabels_left(list(prosumer_cost.keys()), data[0])

    prosumer_cost_compensations = outputs['member_cost_compensations']
    data = pd.DataFrame.from_dict(prosumer_cost_compensations.values())
    data.index = prosumer_cost_compensations.keys()
    plt.bar(list(prosumer_cost_compensations.keys()), data[0], align='edge', width=width_bar, label='member cost compensations')
    addlabels_right(list(prosumer_cost_compensations.keys()), data[0])

    plt.legend(loc="upper right", fontsize=12)
    ax1.set_axisbelow(True)
    ax1.yaxis.grid(color='gray', linestyle='-', alpha=0.5)
    plt.savefig(outputs_dir + 'REC_costs_member', bbox_inches='tight')


