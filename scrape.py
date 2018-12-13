from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from collections import OrderedDict
import pandas as pd
import numpy as np
import pickle


def log_page_ids():
    pg1 = [25692, 25701, 25705, 25707, 25708, 25710, 25713, 25714, 25727, 25735, 25747, 25760, 25768, 25829, 25830, 25834, 25836, 84711, 84712, 84714, 25837, 25838, 99928, 100246, 95332, 95333, 95334, 103843, 103844, 103845, 103846, 103847, 103849, 103850, 103851, 103854, 113666, 109185, 113591, 104320, 113592, 139124, 121712, 121713, 121715, 121716, 93458, 93470, 93482, 93495]

    # print('Count page 1: ', len(pg1))

    pg2 = [93501, 93503, 93505, 153842, 153843, 153844, 153845, 153847, 153850, 153852, 153854, 153855, 167194, 154681, 162321, 161868, 153977, 172096, 172097, 172098, 174678, 172099, 172100, 172101, 174679, 174680, 172102, 192021, 174681, 173972, 174682, 207949, 207951, 207953, 207955, 207959, 207965, 207969, 207973, 207975, 231351, 225417, 203137, 209469, 218865, 240555, 244305, 244309, 244313, 244317]

    # print('Count page 2: ', len(pg2))

    pg3 = [181976, 181980, 181991, 182001, 236305, 236313, 236319, 279705, 279707, 279709, 289293, 268575, 268577, 268579, 289301, 281091, 268581, 281641, 287069, 281645, 287071, 295032, 268583, 268585, 268587, 294309, 268589, 268591, 268593, 295078, 295079, 294312, 294420, 294422]

    # print('Count page 3: ', len(pg3))

    full_lst = pg1 + pg2 + pg3

    # print('\n### FULL LIST ###\nCount: ', len(full_lst))
    # print('\n', full_lst)
    return full_lst


def parse_match(url):
    valid = True
    print('### launching driver ###\n')
    driver = webdriver.Chrome()
    driver.get(url)
    print('### extracting meta details ###\n')
    #extract id
    temp = url.split('.')
    match_id = int(temp[2].split('/')[-1])
    # Tournament, location, date, time
    match_details = driver.find_element_by_class_name("liveSubNavText").text
    # Half-time / full-time scores
    score = driver.find_element_by_class_name("liveSubNavText1").text
    # Click 'Match Stats' tab and extract table details
    rightdiv = driver.find_element_by_xpath('//*[@id="liveRight"]')
    present = len(rightdiv.find_elements_by_xpath('//*[@id="rightDiv"]/ul/li[2]/a')) > 0
    if present == False:
        valid = False
        print('No match stats for: ', driver.current_url)
        return match_id, match_details, score, np.full(76, np.nan), valid

    second_tab = rightdiv.find_element_by_xpath('//*[@id="rightDiv"]/ul/li[2]/a').text

    if second_tab != 'MATCH STATS':
        valid = False
        print('No match stats for: ', driver.current_url)
        return match_id, match_details, score, np.full(76, np.nan), valid

    print('### scraping scorecard ###\n')
    rightdiv.find_element_by_xpath('//*[@id="rightDiv"]/ul/li[2]/a').click()
    tds = rightdiv.find_elements_by_tag_name('td')
    lst = [td.text for td in tds]
    stats = list(filter(None, lst))

    driver.close()

    return match_id, match_details, score, stats, valid

def return_flags(stats):
    home = False
    away = False
    short = False
    med = False
    lng = False
    if stats[0] == 'New Zealand':
        home = True
    if stats[2] == 'New Zealand':
        away = True
    if len(stats) == 71:
        short = True
    if len(stats) == 74:
        med = True
    if len(stats) == 77:
        lng = True

    return home, away, short, med, lng

def create_row_dict(match_id, match_details, score, stats, home=False, away=False, short=False, med=False, lng=False):
    row = OrderedDict()
    # meta data
    row['match_id'] = match_id
    row['home_team'] = stats[0]
    row['away_team'] = stats[2]
    row['tournament'] = match_details.split('-')[0].strip()
    row['location'] = match_details.split(' ')[3].strip(',')
    row['date'] = match_details.split(',')[1].strip()
    row['local_time'] = match_details.split(',')[2].split()[0]
    row['gmt_time'] = match_details.split(',')[3].split()[0]
### NZ listed as home team
    if home:
        # scores
        row['nz_half_points'] = int(score.split('-')[0].split()[-2].strip('(').strip(')'))
        row['opp_half_points'] = int(score.split('-')[1].split()[1].strip('(').strip(')'))
        row['nz_final_score'] = int(score.split('-')[0].split()[-1])
        row['opp_final_score'] = int(score.split('-')[1].split()[0])
        if row['nz_final_score'] < row['opp_final_score']:
            row['result'] = 'L'
        elif row['nz_final_score'] == row['opp_final_score']:
            row['result'] = 'D'
        else:
            row['result'] = 'W'
        # general scoring and stats
        if len(stats[3]) > 2:
            row['nz_tries'] = int(stats[3].split()[0]) + int(stats[3].split()[1].strip('('))
        else:
            row['nz_tries'] = int(stats[3])
        if len(stats[5]) > 2:
            row['opp_tries'] = int(stats[5].split()[0]) + int(stats[5].split()[1].strip('('))
        else:
            row['opp_tries'] = int(stats[5])
        row['nz_convers_made'] = int(stats[6].split()[0])
        row['nz_covers_att'] = int(stats[6].split()[2])
        row['opp_convers_made'] = int(stats[8].split()[0])
        row['opp_covers_att'] = int(stats[8].split()[2])
        row['nz_pen_made'] = int(stats[9].split()[0])
        row['nz_pen_att'] = int(stats[9].split()[2])
        row['opp_pen_made'] = int(stats[11].split()[0])
        row['opp_pen_att'] = int(stats[11].split()[2])
        row['nz_kick_goal_perc'] = round(float(stats[12].strip('%')) * .01, 3)
        row['opp_kick_goal_perc'] = round(float(stats[14].strip('%')) * .01, 3)
        row['nz_drop_goal_made'] = int(stats[15].split()[0])
        if len(stats[15].split()) > 1:
            row['nz_drop_goal_miss'] = int(stats[15].split()[1].strip('('))
        else:
            row['nz_drop_goal_miss'] = np.nan
        row['opp_drop_goal_made'] = int(stats[17].split()[0])
        if len(stats[17].split()) > 1:
            row['opp_drop_goal_miss'] = int(stats[17].split()[1].strip('('))
        else:
            row['opp_drop_goal_miss'] = np.nan

        row['nz_kicks_from_hand'] = int(stats[19])
        row['opp_kicks_from_hand'] = int(stats[21])
        row['nz_passes'] = int(stats[22])
        row['opp_passes'] = int(stats[24])
        row['nz_runs'] = int(stats[25])
        row['opp_runs'] = int(stats[27])
        row['nz_metres_run_w_ball'] = int(stats[28])
        row['opp_metres_run_w_ball'] = int(stats[30])
    ### long stats list indices
        if lng:
            # attacking stats
            if len(stats[32].split()) > 1:
                row['nz_possession_1h'] = round(int(stats[32].split('%')[1].strip().strip('(')) * .01, 3)
                row['nz_possession_2h'] = round(int(stats[32].split('%')[2].strip('/')) * .01, 3)
                row['nz_possession_total'] = round(int(stats[32].split('%')[0]) * .01, 3)
            else:
                row['nz_possession_1h'] = np.nan
                row['nz_possession_2h'] = np.nan
                row['nz_possession_total'] = round(int(stats[32].split('%')[0]) * .01, 3)
            if len(stats[34].split()) > 1:
                row['opp_possession_1h'] = round(int(stats[34].split('%')[1].strip().strip('(')) * .01, 3)
                row['opp_possession_2h'] = round(int(stats[34].split('%')[2].strip('/')) * .01, 3)
                row['opp_possession_total'] = round(int(stats[34].split('%')[0]) * .01, 3)
            else:
                row['opp_possession_1h'] = np.nan
                row['opp_possession_2h'] = np.nan
                row['opp_possession_total'] = round(int(stats[34].split('%')[0]) * .01, 3)

            if len(stats[35].split()) > 1:
                row['nz_territory_1h'] = round(int(stats[35].split('%')[1].strip().strip('(')) * .01, 3)
                row['nz_territory_2h'] = round(int(stats[35].split('%')[2].strip('/')) * .01, 3)
                row['nz_territory_total'] = round(int(stats[35].split('%')[0]) * .01, 3)
            else:
                row['nz_territory_1h'] = np.nan
                row['nz_territory_2h'] = np.nan
                row['nz_territory_total'] = round(int(stats[35].split('%')[0]) * .01, 3)
            if len(stats[37].split()) > 1:
                row['opp_territory_1h'] = round(int(stats[37].split('%')[1].strip().strip('(')) * .01, 3)
                row['opp_territory_2h'] = round(int(stats[37].split('%')[2].strip('/')) * .01, 3)
                row['opp_territory_total'] = round(int(stats[37].split('%')[0]) * .01, 3)
            else:
                row['opp_territory_1h'] = np.nan
                row['opp_territory_2h'] = np.nan
                row['opp_territory_total'] = round(int(stats[37].split('%')[0]) * .01, 3)

            row['nz_clean_breaks'] = int(stats[38])
            row['opp_clean_breaks'] = int(stats[40])
            row['nz_defenders_beat'] = int(stats[41])
            row['opp_defenders_beat'] = int(stats[43])
            row['nz_offloads'] = int(stats[44])
            row['opp_offloads'] = int(stats[46])
            row['nz_rucks_total'] = int(stats[47].split()[2])
            row['nz_rucks_won'] = int(stats[47].split()[0])
            row['nz_rucks_lost'] = row['nz_rucks_total'] - row['nz_rucks_won']
            row['nz_rucks_perc'] = round(float(row['nz_rucks_won'] / row['nz_rucks_total']),3)
            row['opp_rucks_total'] = int(stats[49].split()[2])
            row['opp_rucks_won'] = int(stats[49].split()[0])
            row['opp_rucks_lost'] = row['opp_rucks_total'] - row['opp_rucks_won']
            row['opp_rucks_perc'] = round(float(row['opp_rucks_won'] / row['opp_rucks_total']),3)
            row['nz_maul_total'] = int(stats[50].split()[2])
            row['nz_maul_won'] = int(stats[50].split()[0])
            row['nz_maul_lost'] = row['nz_maul_total'] - row['nz_maul_won']
            if row['nz_maul_total'] != 0:
                row['nz_maul_perc'] = round(float(row['nz_maul_won'] / row['nz_maul_total']),3)
            else:
                row['nz_maul_perc'] = np.nan
            row['opp_maul_total'] = int(stats[52].split()[2])
            row['opp_maul_won'] = int(stats[52].split()[0])
            row['opp_maul_lost'] = row['opp_maul_total'] - row['opp_maul_won']
            if row['opp_maul_total'] != 0:
                row['opp_maul_perc'] = round(float(row['opp_maul_won'] / row['opp_maul_total']),3)
            else:
                row['opp_maul_perc'] = np.nan
            row['nz_turnovers_conceded'] = int(stats[53])
            row['opp_turnovers_conceded'] = int(stats[55])
            # defensive stats
            row['nz_tackles_made'] = int(stats[57].split('/')[0])
            row['nz_tackles_miss'] = int(stats[57].split('/')[1])
            row['nz_tackles_total'] = row['nz_tackles_made'] + row['nz_tackles_miss']
            row['nz_tackles_perc'] = round(float(row['nz_tackles_made'] / row['nz_tackles_total']),3)
            row['opp_tackles_made'] = int(stats[59].split('/')[0])
            row['opp_tackles_miss'] = int(stats[59].split('/')[1])
            row['opp_tackles_total'] = row['opp_tackles_made'] + row['opp_tackles_miss']
            row['opp_tackles_perc'] = round(float(row['opp_tackles_made'] / row['opp_tackles_total']),3)
            # set pieces
            row['nz_scrums_own_won'] = int(stats[64].split()[0])
            row['nz_scrums_own_lost'] = int(stats[64].split()[2])
            row['nz_scrums_own_total'] = row['nz_scrums_own_won'] + row['nz_scrums_own_lost']
            row['nz_scrums_own_perc'] = round(float(row['nz_scrums_own_won'] / row['nz_scrums_own_total']), 3)
            row['opp_scrums_own_won'] = int(stats[66].split()[0])
            row['opp_scrums_own_lost'] = int(stats[66].split()[2])
            row['opp_scrums_own_total'] = row['opp_scrums_own_won'] + row['opp_scrums_own_lost']
            row['opp_scrums_own_perc'] = round(float(row['opp_scrums_own_won'] / row['opp_scrums_own_total']), 3)

            row['nz_lineout_own_won'] = int(stats[67].split()[0])
            row['nz_lineout_own_lost'] = int(stats[67].split()[2])
            row['nz_lineout_own_total'] = row['nz_lineout_own_won'] + row['nz_lineout_own_lost']
            row['nz_lineout_own_perc'] = round(float(row['nz_lineout_own_won'] / row['nz_lineout_own_total']), 3)
            row['opp_lineout_own_won'] = int(stats[69].split()[0])
            row['opp_lineout_own_lost'] = int(stats[69].split()[2])
            row['opp_lineout_own_total'] = row['opp_lineout_own_won'] + row['opp_lineout_own_lost']
            row['opp_lineout_own_perc'] = round(float(row['opp_lineout_own_won'] / row['opp_lineout_own_total']), 3)
            # discipline
            row['nz_pen_conceded'] = int(stats[71].split()[0])
            row['opp_pen_conceded'] = int(stats[73].split()[0])
            if stats[72] == 'Penalties conceded (Freekicks)':
                row['nz_freekick_conceded'] = int(stats[71].split()[1].strip('(').strip(')'))
                row['opp_freekick_conceded'] = int(stats[73].split()[1].strip('(').strip(')'))
            else:
                row['nz_freekick_conceded'] = np.nan
                row['opp_freekick_conceded'] = np.nan

            row['nz_yellow_card'] = int(stats[74].split('/')[0])
            row['nz_red_card'] = int(stats[74].split('/')[1])
            row['opp_yellow_card'] = int(stats[76].split('/')[0])
            row['opp_red_card'] = int(stats[76].split('/')[1])

    ## med stats list index
        if med:
            # attacking stats
            row['nz_territory_1h'] = np.nan
            row['nz_territory_2h'] = np.nan
            row['nz_territory_total'] = np.nan
            row['opp_territory_1h'] = np.nan
            row['opp_territory_2h'] = np.nan
            row['opp_territory_total'] = np.nan

            if len(stats[32].split()) > 1:
                row['nz_possession_1h'] = round(int(stats[32].split('%')[1].strip().strip('(')) * .01, 3)
                row['nz_possession_2h'] = round(int(stats[32].split('%')[2].strip('/')) * .01, 3)
                row['nz_possession_total'] = round(int(stats[32].split('%')[0]) * .01, 3)
            else:
                row['nz_possession_1h'] = np.nan
                row['nz_possession_2h'] = np.nan
                row['nz_possession_total'] = round(int(stats[32].split('%')[0]) * .01, 3)
            if len(stats[34].split()) > 1:
                row['opp_possession_1h'] = round(int(stats[34].split('%')[1].strip().strip('(')) * .01, 3)
                row['opp_possession_2h'] = round(int(stats[34].split('%')[2].strip('/')) * .01, 3)
                row['opp_possession_total'] = round(int(stats[34].split('%')[0]) * .01, 3)
            else:
                row['opp_possession_1h'] = np.nan
                row['opp_possession_2h'] = np.nan
                row['opp_possession_total'] = round(int(stats[34].split('%')[0]) * .01, 3)

            row['nz_clean_breaks'] = int(stats[35])
            row['opp_clean_breaks'] = int(stats[37])
            row['nz_defenders_beat'] = int(stats[38])
            row['opp_defenders_beat'] = int(stats[40])
            row['nz_offloads'] = int(stats[41])
            row['opp_offloads'] = int(stats[43])
            row['nz_rucks_total'] = int(stats[44].split()[2])
            row['nz_rucks_won'] = int(stats[44].split()[0])
            row['nz_rucks_lost'] = row['nz_rucks_total'] - row['nz_rucks_won']
            row['nz_rucks_perc'] = round(float(row['nz_rucks_won'] / row['nz_rucks_total']),3)
            row['opp_rucks_total'] = int(stats[46].split()[2])
            row['opp_rucks_won'] = int(stats[46].split()[0])
            row['opp_rucks_lost'] = row['opp_rucks_total'] - row['opp_rucks_won']
            row['opp_rucks_perc'] = round(float(row['opp_rucks_won'] / row['opp_rucks_total']),3)
            row['nz_maul_total'] = int(stats[47].split()[2])
            row['nz_maul_won'] = int(stats[47].split()[0])
            row['nz_maul_lost'] = row['nz_maul_total'] - row['nz_maul_won']
            if row['nz_maul_total'] != 0:
                row['nz_maul_perc'] = round(float(row['nz_maul_won'] / row['nz_maul_total']),3)
            else:
                row['nz_maul_perc'] = np.nan
            row['opp_maul_total'] = int(stats[49].split()[2])
            row['opp_maul_won'] = int(stats[49].split()[0])
            row['opp_maul_lost'] = row['opp_maul_total'] - row['opp_maul_won']
            if row['opp_maul_total'] != 0:
                row['opp_maul_perc'] = round(float(row['opp_maul_won'] / row['opp_maul_total']),3)
            else:
                row['opp_maul_perc'] = np.nan
            row['nz_turnovers_conceded'] = int(stats[50])
            row['opp_turnovers_conceded'] = int(stats[52])
            # defensive stats
            row['nz_tackles_made'] = int(stats[54].split('/')[0])
            row['nz_tackles_miss'] = int(stats[54].split('/')[1])
            row['nz_tackles_total'] = row['nz_tackles_made'] + row['nz_tackles_miss']
            row['nz_tackles_perc'] = round(float(row['nz_tackles_made'] / row['nz_tackles_total']),3)
            row['opp_tackles_made'] = int(stats[56].split('/')[0])
            row['opp_tackles_miss'] = int(stats[56].split('/')[1])
            row['opp_tackles_total'] = row['opp_tackles_made'] + row['opp_tackles_miss']
            row['opp_tackles_perc'] = round(float(row['opp_tackles_made'] / row['opp_tackles_total']),3)
            # set pieces
            row['nz_scrums_own_won'] = int(stats[61].split()[0])
            row['nz_scrums_own_lost'] = int(stats[61].split()[2])
            row['nz_scrums_own_total'] = row['nz_scrums_own_won'] + row['nz_scrums_own_lost']
            row['nz_scrums_own_perc'] = round(float(row['nz_scrums_own_won'] / row['nz_scrums_own_total']), 3)
            row['opp_scrums_own_won'] = int(stats[63].split()[0])
            row['opp_scrums_own_lost'] = int(stats[63].split()[2])
            row['opp_scrums_own_total'] = row['opp_scrums_own_won'] + row['opp_scrums_own_lost']
            row['opp_scrums_own_perc'] = round(float(row['opp_scrums_own_won'] / row['opp_scrums_own_total']), 3)

            row['nz_lineout_own_won'] = int(stats[64].split()[0])
            row['nz_lineout_own_lost'] = int(stats[64].split()[2])
            row['nz_lineout_own_total'] = row['nz_lineout_own_won'] + row['nz_lineout_own_lost']
            row['nz_lineout_own_perc'] = round(float(row['nz_lineout_own_won'] / row['nz_lineout_own_total']), 3)
            row['opp_lineout_own_won'] = int(stats[66].split()[0])
            row['opp_lineout_own_lost'] = int(stats[66].split()[2])
            row['opp_lineout_own_total'] = row['opp_lineout_own_won'] + row['opp_lineout_own_lost']
            row['opp_lineout_own_perc'] = round(float(row['opp_lineout_own_won'] / row['opp_lineout_own_total']), 3)
            # discipline
            row['nz_pen_conceded'] = int(stats[68].split()[0])
            row['opp_pen_conceded'] = int(stats[70].split()[0])
            if stats[69] == 'Penalties conceded (Freekicks)':
                row['nz_freekick_conceded'] = int(stats[68].split()[1].strip('(').strip(')'))
                row['opp_freekick_conceded'] = int(stats[70].split()[1].strip('(').strip(')'))
            else:
                row['nz_freekick_conceded'] = np.nan
                row['opp_freekick_conceded'] = np.nan
            row['nz_yellow_card'] = int(stats[71].split('/')[0])
            row['nz_red_card'] = int(stats[71].split('/')[1])
            row['opp_yellow_card'] = int(stats[73].split('/')[0])
            row['opp_red_card'] = int(stats[73].split('/')[1])

    ### short stats list
        if short:
            # attacking stats
            row['nz_possession_1h'] = np.nan
            row['nz_possession_2h'] = np.nan
            row['nz_possession_total'] = np.nan
            row['opp_possession_1h'] = np.nan
            row['opp_possession_2h'] = np.nan
            row['opp_possession_total'] = np.nan
            row['nz_territory_1h'] = np.nan
            row['nz_territory_2h'] = np.nan
            row['nz_territory_total'] = np.nan
            row['opp_territory_1h'] = np.nan
            row['opp_territory_2h'] = np.nan
            row['opp_territory_total'] = np.nan

            row['nz_clean_breaks'] = int(stats[32])
            row['opp_clean_breaks'] = int(stats[34])
            row['nz_defenders_beat'] = int(stats[35])
            row['opp_defenders_beat'] = int(stats[37])
            row['nz_offloads'] = int(stats[38])
            row['opp_offloads'] = int(stats[40])
            row['nz_rucks_total'] = int(stats[41].split()[2])
            row['nz_rucks_won'] = int(stats[41].split()[0])
            row['nz_rucks_lost'] = row['nz_rucks_total'] - row['nz_rucks_won']
            row['nz_rucks_perc'] = round(float(row['nz_rucks_won'] / row['nz_rucks_total']),3)
            row['opp_rucks_total'] = int(stats[43].split()[2])
            row['opp_rucks_won'] = int(stats[43].split()[0])
            row['opp_rucks_lost'] = row['opp_rucks_total'] - row['opp_rucks_won']
            row['opp_rucks_perc'] = round(float(row['opp_rucks_won'] / row['opp_rucks_total']),3)
            row['nz_maul_total'] = int(stats[44].split()[2])
            row['nz_maul_won'] = int(stats[44].split()[0])
            row['nz_maul_lost'] = row['nz_maul_total'] - row['nz_maul_won']
            if row['nz_maul_total'] != 0:
                row['nz_maul_perc'] = round(float(row['nz_maul_won'] / row['nz_maul_total']),3)
            else:
                row['nz_maul_perc'] = np.nan
            row['opp_maul_total'] = int(stats[46].split()[2])
            row['opp_maul_won'] = int(stats[46].split()[0])
            row['opp_maul_lost'] = row['opp_maul_total'] - row['opp_maul_won']
            if row['opp_maul_total'] != 0:
                row['opp_maul_perc'] = round(float(row['opp_maul_won'] / row['opp_maul_total']),3)
            else:
                row['opp_maul_perc'] = np.nan
            row['nz_turnovers_conceded'] = int(stats[47])
            row['opp_turnovers_conceded'] = int(stats[49])
            # defensive stats
            row['nz_tackles_made'] = int(stats[51].split('/')[0])
            row['nz_tackles_miss'] = int(stats[51].split('/')[1])
            row['nz_tackles_total'] = row['nz_tackles_made'] + row['nz_tackles_miss']
            row['nz_tackles_perc'] = round(float(row['nz_tackles_made'] / row['nz_tackles_total']),3)
            row['opp_tackles_made'] = int(stats[53].split('/')[0])
            row['opp_tackles_miss'] = int(stats[53].split('/')[1])
            row['opp_tackles_total'] = row['opp_tackles_made'] + row['opp_tackles_miss']
            row['opp_tackles_perc'] = round(float(row['opp_tackles_made'] / row['opp_tackles_total']),3)
            # set pieces
            row['nz_scrums_own_won'] = int(stats[58].split()[0])
            row['nz_scrums_own_lost'] = int(stats[58].split()[2])
            row['nz_scrums_own_total'] = row['nz_scrums_own_won'] + row['nz_scrums_own_lost']
            row['nz_scrums_own_perc'] = round(float(row['nz_scrums_own_won'] / row['nz_scrums_own_total']), 3)
            row['opp_scrums_own_won'] = int(stats[60].split()[0])
            row['opp_scrums_own_lost'] = int(stats[60].split()[2])
            row['opp_scrums_own_total'] = row['opp_scrums_own_won'] + row['opp_scrums_own_lost']
            row['opp_scrums_own_perc'] = round(float(row['opp_scrums_own_won'] / row['opp_scrums_own_total']), 3)

            row['nz_lineout_own_won'] = int(stats[61].split()[0])
            row['nz_lineout_own_lost'] = int(stats[61].split()[2])
            row['nz_lineout_own_total'] = row['nz_lineout_own_won'] + row['nz_lineout_own_lost']
            row['nz_lineout_own_perc'] = round(float(row['nz_lineout_own_won'] / row['nz_lineout_own_total']), 3)
            row['opp_lineout_own_won'] = int(stats[63].split()[0])
            row['opp_lineout_own_lost'] = int(stats[63].split()[2])
            row['opp_lineout_own_total'] = row['opp_lineout_own_won'] + row['opp_lineout_own_lost']
            row['opp_lineout_own_perc'] = round(float(row['opp_lineout_own_won'] / row['opp_lineout_own_total']), 3)
            # discipline
            row['nz_pen_conceded'] = int(stats[65].split()[0])
            row['opp_pen_conceded'] = int(stats[67].split()[0])
            if stats[66] == 'Penalties conceded (Freekicks)':
                row['nz_freekick_conceded'] = int(stats[65].split()[1].strip('(').strip(')'))
                row['opp_freekick_conceded'] = int(stats[67].split()[1].strip('(').strip(')'))
            else:
                row['nz_freekick_conceded'] = np.nan
                row['opp_freekick_conceded'] = np.nan
            row['nz_yellow_card'] = int(stats[68].split('/')[0])
            row['nz_red_card'] = int(stats[68].split('/')[1])
            row['opp_yellow_card'] = int(stats[70].split('/')[0])
            row['opp_red_card'] = int(stats[70].split('/')[1])

### NZ listed as away team
    if away:
        row['opp_half_points'] = int(score.split('-')[0].split()[-2].strip('(').strip(')'))
        row['nz_half_points'] = int(score.split('-')[1].split()[1].strip('(').strip(')'))
        row['opp_final_score'] = int(score.split('-')[0].split()[-1])
        row['nz_final_score'] = int(score.split('-')[1].split()[0])
        if row['nz_final_score'] < row['opp_final_score']:
            row['result'] = 'L'
        elif row['nz_final_score'] == row['opp_final_score']:
            row['result'] = 'D'
        else:
            row['result'] = 'W'
        # general scoring and stats
        if len(stats[3]) > 2:
            row['opp_tries'] = int(stats[3].split()[0]) + int(stats[3].split()[1].strip('('))
        else:
            row['opp_tries'] = int(stats[3])
        if len(stats[5]) > 2:
            row['nz_tries'] = int(stats[5].split()[0]) + int(stats[5].split()[1].strip('('))
        else:
            row['nz_tries'] = int(stats[5])
        row['opp_convers_made'] = int(stats[6].split()[0])
        row['opp_covers_att'] = int(stats[6].split()[2])
        row['nz_convers_made'] = int(stats[8].split()[0])
        row['nz_covers_att'] = int(stats[8].split()[2])
        row['opp_pen_made'] = int(stats[9].split()[0])
        row['opp_pen_att'] = int(stats[9].split()[2])
        row['nz_pen_made'] = int(stats[11].split()[0])
        row['nz_pen_att'] = int(stats[11].split()[2])
        row['opp_kick_goal_perc'] = round(float(stats[12].strip('%')) * .01, 3)
        row['nz_kick_goal_perc'] = round(float(stats[14].strip('%')) * .01, 3)
        row['opp_drop_goal_made'] = int(stats[15].split()[0])
        if len(stats[15].split()) > 1:
            row['opp_drop_goal_miss'] = int(stats[15].split()[1].strip('('))
        else:
            row['opp_drop_goal_miss'] = np.nan
        row['nz_drop_goal_made'] = int(stats[17].split()[0])
        if len(stats[17].split()) > 1:
            row['nz_drop_goal_miss'] = int(stats[17].split()[1].strip('('))
        else:
            row['nz_drop_goal_miss'] = np.nan

        row['opp_kicks_from_hand'] = int(stats[19])
        row['nz_kicks_from_hand'] = int(stats[21])
        row['opp_passes'] = int(stats[22])
        row['nz_passes'] = int(stats[24])
        row['opp_runs'] = int(stats[25])
        row['nz_runs'] = int(stats[27])
        row['opp_metres_run_w_ball'] = int(stats[28])
        row['nz_metres_run_w_ball'] = int(stats[30])

    ### long stats list indices
        if lng:
            # attacking stats
            if len(stats[32].split()) > 1:
                row['opp_possession_1h'] = round(int(stats[32].split('%')[1].strip().strip('(')) * .01, 3)
                row['opp_possession_2h'] = round(int(stats[32].split('%')[2].strip('/')) * .01, 3)
                row['opp_possession_total'] = round(int(stats[32].split('%')[0]) * .01, 3)
            else:
                row['opp_possession_1h'] = np.nan
                row['opp_possession_2h'] = np.nan
                row['opp_possession_total'] = round(int(stats[32].split('%')[0]) * .01, 3)
            if len(stats[34].split()) > 1:
                row['nz_possession_1h'] = round(int(stats[34].split('%')[1].strip().strip('(')) * .01, 3)
                row['nz_possession_2h'] = round(int(stats[34].split('%')[2].strip('/')) * .01, 3)
                row['nz_possession_total'] = round(int(stats[34].split('%')[0]) * .01, 3)
            else:
                row['nz_possession_1h'] = np.nan
                row['nz_possession_2h'] = np.nan
                row['nz_possession_total'] = round(int(stats[34].split('%')[0]) * .01, 3)

            if len(stats[35].split()) > 1:
                row['opp_territory_1h'] = round(int(stats[35].split('%')[1].strip().strip('(')) * .01, 3)
                row['opp_territory_2h'] = round(int(stats[35].split('%')[2].strip('/')) * .01, 3)
                row['opp_territory_total'] = round(int(stats[35].split('%')[0]) * .01, 3)
            else:
                row['opp_territory_1h'] = np.nan
                row['opp_territory_2h'] = np.nan
                row['opp_territory_total'] = round(int(stats[35].split('%')[0]) * .01, 3)
            if len(stats[37].split()) > 1:
                row['nz_territory_1h'] = round(int(stats[37].split('%')[1].strip().strip('(')) * .01, 3)
                row['nz_territory_2h'] = round(int(stats[37].split('%')[2].strip('/')) * .01, 3)
                row['nz_territory_total'] = round(int(stats[37].split('%')[0]) * .01, 3)
            else:
                row['nz_territory_1h'] = np.nan
                row['nz_territory_2h'] = np.nan
                row['nz_territory_total'] = round(int(stats[37].split('%')[0]) * .01, 3)

            row['opp_clean_breaks'] = int(stats[38])
            row['nz_clean_breaks'] = int(stats[40])
            row['opp_defenders_beat'] = int(stats[41])
            row['nz_defenders_beat'] = int(stats[43])
            row['opp_offloads'] = int(stats[44])
            row['nz_offloads'] = int(stats[46])
            row['opp_rucks_total'] = int(stats[47].split()[2])
            row['opp_rucks_won'] = int(stats[47].split()[0])
            row['opp_rucks_lost'] = row['opp_rucks_total'] - row['opp_rucks_won']
            row['opp_rucks_perc'] = round(float(row['opp_rucks_won'] / row['opp_rucks_total']),3)
            row['nz_rucks_total'] = int(stats[49].split()[2])
            row['nz_rucks_won'] = int(stats[49].split()[0])
            row['nz_rucks_lost'] = row['nz_rucks_total'] - row['nz_rucks_won']
            row['nz_rucks_perc'] = round(float(row['nz_rucks_won'] / row['nz_rucks_total']),3)
            row['opp_maul_total'] = int(stats[50].split()[2])
            row['opp_maul_won'] = int(stats[50].split()[0])
            row['opp_maul_lost'] = row['opp_maul_total'] - row['opp_maul_won']
            if row['opp_maul_total'] != 0:
                row['opp_maul_perc'] = round(float(row['opp_maul_won'] / row['opp_maul_total']),3)
            else:
                row['opp_maul_perc'] = np.nan
            row['nz_maul_total'] = int(stats[52].split()[2])
            row['nz_maul_won'] = int(stats[52].split()[0])
            row['nz_maul_lost'] = row['nz_maul_total'] - row['nz_maul_won']
            if row['nz_maul_total'] != 0:
                row['nz_maul_perc'] = round(float(row['nz_maul_won'] / row['nz_maul_total']),3)
            else:
                row['nz_maul_perc'] = np.nan
            row['opp_turnovers_conceded'] = int(stats[53])
            row['nz_turnovers_conceded'] = int(stats[55])
            # defensive stats
            row['opp_tackles_made'] = int(stats[57].split('/')[0])
            row['opp_tackles_miss'] = int(stats[57].split('/')[1])
            row['opp_tackles_total'] = row['opp_tackles_made'] + row['opp_tackles_miss']
            row['opp_tackles_perc'] = round(float(row['opp_tackles_made'] / row['opp_tackles_total']),3)
            row['nz_tackles_made'] = int(stats[59].split('/')[0])
            row['nz_tackles_miss'] = int(stats[59].split('/')[1])
            row['nz_tackles_total'] = row['nz_tackles_made'] + row['nz_tackles_miss']
            row['nz_tackles_perc'] = round(float(row['nz_tackles_made'] / row['nz_tackles_total']),3)
            # set pieces
            row['opp_scrums_own_won'] = int(stats[64].split()[0])
            row['opp_scrums_own_lost'] = int(stats[64].split()[2])
            row['opp_scrums_own_total'] = row['opp_scrums_own_won'] + row['opp_scrums_own_lost']
            row['opp_scrums_own_perc'] = round(float(row['opp_scrums_own_won'] / row['opp_scrums_own_total']), 3)
            row['nz_scrums_own_won'] = int(stats[66].split()[0])
            row['nz_scrums_own_lost'] = int(stats[66].split()[2])
            row['nz_scrums_own_total'] = row['nz_scrums_own_won'] + row['nz_scrums_own_lost']
            row['nz_scrums_own_perc'] = round(float(row['nz_scrums_own_won'] / row['nz_scrums_own_total']), 3)

            row['opp_lineout_own_won'] = int(stats[67].split()[0])
            row['opp_lineout_own_lost'] = int(stats[67].split()[2])
            row['opp_lineout_own_total'] = row['opp_lineout_own_won'] + row['opp_lineout_own_lost']
            row['opp_lineout_own_perc'] = round(float(row['opp_lineout_own_won'] / row['opp_lineout_own_total']), 3)
            row['nz_lineout_own_won'] = int(stats[69].split()[0])
            row['nz_lineout_own_lost'] = int(stats[69].split()[2])
            row['nz_lineout_own_total'] = row['nz_lineout_own_won'] + row['nz_lineout_own_lost']
            row['nz_lineout_own_perc'] = round(float(row['nz_lineout_own_won'] / row['nz_lineout_own_total']), 3)
            # discipline
            row['opp_pen_conceded'] = int(stats[71].split()[0])
            row['nz_pen_conceded'] = int(stats[73].split()[0])
            if stats[72] == 'Penalties conceded (Freekicks)':
                row['opp_freekick_conceded'] = int(stats[71].split()[1].strip('(').strip(')'))
                row['nz_freekick_conceded'] = int(stats[73].split()[1].strip('(').strip(')'))
            else:
                row['opp_freekick_conceded'] = np.nan
                row['nz_freekick_conceded'] = np.nan
            row['opp_yellow_card'] = int(stats[74].split('/')[0])
            row['opp_red_card'] = int(stats[74].split('/')[1])
            row['nz_yellow_card'] = int(stats[76].split('/')[0])
            row['nz_red_card'] = int(stats[76].split('/')[1])

    ### med stats list index
        if med:
            # attacking stats
            row['nz_territory_1h'] = np.nan
            row['nz_territory_2h'] = np.nan
            row['nz_territory_total'] = np.nan
            row['opp_territory_1h'] = np.nan
            row['opp_territory_2h'] = np.nan
            row['opp_territory_total'] = np.nan

            if len(stats[32].split()) > 1:
                row['opp_possession_1h'] = round(int(stats[32].split('%')[1].strip().strip('(')) * .01, 3)
                row['opp_possession_2h'] = round(int(stats[32].split('%')[2].strip('/')) * .01, 3)
                row['opp_possession_total'] = round(int(stats[32].split('%')[0]) * .01, 3)
            else:
                row['opp_possession_1h'] = np.nan
                row['opp_possession_2h'] = np.nan
                row['opp_possession_total'] = round(int(stats[32].split('%')[0]) * .01, 3)
            if len(stats[34].split()) > 1:
                row['nz_possession_1h'] = round(int(stats[34].split('%')[1].strip().strip('(')) * .01, 3)
                row['nz_possession_2h'] = round(int(stats[34].split('%')[2].strip('/')) * .01, 3)
                row['nz_possession_total'] = round(int(stats[34].split('%')[0]) * .01, 3)
            else:
                row['nz_possession_1h'] = np.nan
                row['nz_possession_2h'] = np.nan
                row['nz_possession_total'] = round(int(stats[34].split('%')[0]) * .01, 3)

            row['opp_clean_breaks'] = int(stats[35])
            row['nz_clean_breaks'] = int(stats[37])
            row['opp_defenders_beat'] = int(stats[38])
            row['nz_defenders_beat'] = int(stats[40])
            row['opp_offloads'] = int(stats[41])
            row['nz_offloads'] = int(stats[43])
            row['opp_rucks_total'] = int(stats[44].split()[2])
            row['opp_rucks_won'] = int(stats[44].split()[0])
            row['opp_rucks_lost'] = row['opp_rucks_total'] - row['opp_rucks_won']
            row['opp_rucks_perc'] = round(float(row['opp_rucks_won'] / row['opp_rucks_total']),3)
            row['nz_rucks_total'] = int(stats[46].split()[2])
            row['nz_rucks_won'] = int(stats[46].split()[0])
            row['nz_rucks_lost'] = row['nz_rucks_total'] - row['nz_rucks_won']
            row['nz_rucks_perc'] = round(float(row['nz_rucks_won'] / row['nz_rucks_total']),3)
            row['opp_maul_total'] = int(stats[47].split()[2])
            row['opp_maul_won'] = int(stats[47].split()[0])
            row['opp_maul_lost'] = row['opp_maul_total'] - row['opp_maul_won']
            if row['opp_maul_total'] != 0:
                row['opp_maul_perc'] = round(float(row['opp_maul_won'] / row['opp_maul_total']),3)
            else:
                row['opp_maul_perc'] = np.nan
            row['nz_maul_total'] = int(stats[49].split()[2])
            row['nz_maul_won'] = int(stats[49].split()[0])
            row['nz_maul_lost'] = row['nz_maul_total'] - row['nz_maul_won']
            if row['nz_maul_total'] != 0:
                row['nz_maul_perc'] = round(float(row['nz_maul_won'] / row['nz_maul_total']),3)
            else:
                row['nz_maul_perc'] = np.nan
            row['opp_turnovers_conceded'] = int(stats[50])
            row['nz_turnovers_conceded'] = int(stats[52])
            # defensive stats
            row['opp_tackles_made'] = int(stats[54].split('/')[0])
            row['opp_tackles_miss'] = int(stats[54].split('/')[1])
            row['opp_tackles_total'] = row['opp_tackles_made'] + row['opp_tackles_miss']
            row['opp_tackles_perc'] = round(float(row['opp_tackles_made'] / row['opp_tackles_total']),3)
            row['nz_tackles_made'] = int(stats[56].split('/')[0])
            row['nz_tackles_miss'] = int(stats[56].split('/')[1])
            row['nz_tackles_total'] = row['nz_tackles_made'] + row['nz_tackles_miss']
            row['nz_tackles_perc'] = round(float(row['nz_tackles_made'] / row['nz_tackles_total']),3)
            # set pieces
            row['opp_scrums_own_won'] = int(stats[61].split()[0])
            row['opp_scrums_own_lost'] = int(stats[61].split()[2])
            row['opp_scrums_own_total'] = row['opp_scrums_own_won'] + row['opp_scrums_own_lost']
            row['opp_scrums_own_perc'] = round(float(row['opp_scrums_own_won'] / row['opp_scrums_own_total']), 3)
            row['nz_scrums_own_won'] = int(stats[63].split()[0])
            row['nz_scrums_own_lost'] = int(stats[63].split()[2])
            row['nz_scrums_own_total'] = row['nz_scrums_own_won'] + row['nz_scrums_own_lost']
            row['nz_scrums_own_perc'] = round(float(row['nz_scrums_own_won'] / row['nz_scrums_own_total']), 3)

            row['opp_lineout_own_won'] = int(stats[64].split()[0])
            row['opp_lineout_own_lost'] = int(stats[64].split()[2])
            row['opp_lineout_own_total'] = row['opp_lineout_own_won'] + row['opp_lineout_own_lost']
            row['opp_lineout_own_perc'] = round(float(row['opp_lineout_own_won'] / row['opp_lineout_own_total']), 3)
            row['nz_lineout_own_won'] = int(stats[66].split()[0])
            row['nz_lineout_own_lost'] = int(stats[66].split()[2])
            row['nz_lineout_own_total'] = row['nz_lineout_own_won'] + row['nz_lineout_own_lost']
            row['nz_lineout_own_perc'] = round(float(row['nz_lineout_own_won'] / row['nz_lineout_own_total']), 3)
            # discipline
            row['opp_pen_conceded'] = int(stats[68].split()[0])
            row['nz_pen_conceded'] = int(stats[70].split()[0])
            if stats[69] == 'Penalties conceded (Freekicks)':
                row['opp_freekick_conceded'] = int(stats[68].split()[1].strip('(').strip(')'))
                row['nz_freekick_conceded'] = int(stats[70].split()[1].strip('(').strip(')'))
            else:
                row['opp_freekick_conceded'] = np.nan
                row['nz_freekick_conceded'] = np.nan
            row['opp_yellow_card'] = int(stats[71].split('/')[0])
            row['opp_red_card'] = int(stats[71].split('/')[1])
            row['nz_yellow_card'] = int(stats[73].split('/')[0])
            row['nz_red_card'] = int(stats[73].split('/')[1])

    ### short stats list
        if short:
            row['nz_possession_1h'] = np.nan
            row['nz_possession_2h'] = np.nan
            row['nz_possession_total'] = np.nan
            row['opp_possession_1h'] = np.nan
            row['opp_possession_2h'] = np.nan
            row['opp_possession_total'] = np.nan
            row['nz_territory_1h'] = np.nan
            row['nz_territory_2h'] = np.nan
            row['nz_territory_total'] = np.nan
            row['opp_territory_1h'] = np.nan
            row['opp_territory_2h'] = np.nan
            row['opp_territory_total'] = np.nan

            row['opp_clean_breaks'] = int(stats[32])
            row['nz_clean_breaks'] = int(stats[34])
            row['opp_defenders_beat'] = int(stats[35])
            row['nz_defenders_beat'] = int(stats[37])
            row['opp_offloads'] = int(stats[38])
            row['nz_offloads'] = int(stats[40])
            row['opp_rucks_total'] = int(stats[41].split()[2])
            row['opp_rucks_won'] = int(stats[41].split()[0])
            row['opp_rucks_lost'] = row['opp_rucks_total'] - row['opp_rucks_won']
            row['opp_rucks_perc'] = round(float(row['opp_rucks_won'] / row['opp_rucks_total']),3)
            row['nz_rucks_total'] = int(stats[43].split()[2])
            row['nz_rucks_won'] = int(stats[43].split()[0])
            row['nz_rucks_lost'] = row['nz_rucks_total'] - row['nz_rucks_won']
            row['nz_rucks_perc'] = round(float(row['nz_rucks_won'] / row['nz_rucks_total']),3)
            row['opp_maul_total'] = int(stats[44].split()[2])
            row['opp_maul_won'] = int(stats[44].split()[0])
            row['opp_maul_lost'] = row['opp_maul_total'] - row['opp_maul_won']
            if row['opp_maul_total'] != 0:
                row['opp_maul_perc'] = round(float(row['opp_maul_won'] / row['opp_maul_total']),3)
            else:
                row['opp_maul_perc'] = np.nan
            row['nz_maul_total'] = int(stats[46].split()[2])
            row['nz_maul_won'] = int(stats[46].split()[0])
            row['nz_maul_lost'] = row['nz_maul_total'] - row['nz_maul_won']
            if row['nz_maul_total'] != 0:
                row['nz_maul_perc'] = round(float(row['nz_maul_won'] / row['nz_maul_total']),3)
            else:
                row['nz_maul_perc'] = np.nan
            row['opp_turnovers_conceded'] = int(stats[47])
            row['nz_turnovers_conceded'] = int(stats[49])
        # defensive stats
            row['opp_tackles_made'] = int(stats[51].split('/')[0])
            row['opp_tackles_miss'] = int(stats[51].split('/')[1])
            row['opp_tackles_total'] = row['opp_tackles_made'] + row['opp_tackles_miss']
            row['opp_tackles_perc'] = round(float(row['opp_tackles_made'] / row['opp_tackles_total']),3)
            row['nz_tackles_made'] = int(stats[53].split('/')[0])
            row['nz_tackles_miss'] = int(stats[53].split('/')[1])
            row['nz_tackles_total'] = row['nz_tackles_made'] + row['nz_tackles_miss']
            row['nz_tackles_perc'] = round(float(row['nz_tackles_made'] / row['nz_tackles_total']),3)
        # set pieces
            row['opp_scrums_own_won'] = int(stats[58].split()[0])
            row['opp_scrums_own_lost'] = int(stats[58].split()[2])
            row['opp_scrums_own_total'] = row['opp_scrums_own_won'] + row['opp_scrums_own_lost']
            row['opp_scrums_own_perc'] = round(float(row['opp_scrums_own_won'] / row['opp_scrums_own_total']), 3)
            row['nz_scrums_own_won'] = int(stats[60].split()[0])
            row['nz_scrums_own_lost'] = int(stats[60].split()[2])
            row['nz_scrums_own_total'] = row['nz_scrums_own_won'] + row['nz_scrums_own_lost']
            row['nz_scrums_own_perc'] = round(float(row['nz_scrums_own_won'] / row['nz_scrums_own_total']), 3)

            row['opp_lineout_own_won'] = int(stats[61].split()[0])
            row['opp_lineout_own_lost'] = int(stats[61].split()[2])
            row['opp_lineout_own_total'] = row['opp_lineout_own_won'] + row['opp_lineout_own_lost']
            row['opp_lineout_own_perc'] = round(float(row['opp_lineout_own_won'] / row['opp_lineout_own_total']), 3)
            row['nz_lineout_own_won'] = int(stats[63].split()[0])
            row['nz_lineout_own_lost'] = int(stats[63].split()[2])
            row['nz_lineout_own_total'] = row['nz_lineout_own_won'] + row['nz_lineout_own_lost']
            row['nz_lineout_own_perc'] = round(float(row['nz_lineout_own_won'] / row['nz_lineout_own_total']), 3)
            # discipline
            row['opp_pen_conceded'] = int(stats[65].split()[0])
            row['nz_pen_conceded'] = int(stats[67].split()[0])
            if stats[66] == 'Penalties conceded (Freekicks)':
                row['opp_freekick_conceded'] = int(stats[65].split()[1].strip('(').strip(')'))
                row['nz_freekick_conceded'] = int(stats[67].split()[1].strip('(').strip(')'))
            else:
                row['opp_freekick_conceded'] = np.nan
                row['nz_freekick_conceded'] = np.nan
            row['opp_yellow_card'] = int(stats[68].split('/')[0])
            row['opp_red_card'] = int(stats[68].split('/')[1])
            row['nz_yellow_card'] = int(stats[70].split('/')[0])
            row['nz_red_card'] = int(stats[70].split('/')[1])

    return row


def hammer_time(df, match_id_lst):
    print('### begin hammer time ###\n')
    # loop through the match ids
    for idx, idd in enumerate(match_id_lst):
        print('### begin parsing match idx ', idx, ' ###\n')
        # set url to be passed to selenium
        url = 'http://stats.espnscrum.com/statsguru/rugby/match/' + str(idd) + '.html?view=scorecard'
        # extract initial components
        match_id, match_details, score, stats, valid = parse_match(url)
        if valid == False:
            continue
        # creat flags for row_dict function
        home, away, short, med, lng = return_flags(stats)
        # create row dictionary
        row = create_row_dict(match_id, match_details, score, stats, home, away, short, med, lng)
        # append row to df
        df = df.append(row, ignore_index=True)
        print('### match idx ', idx, ' complete ###\n')

    return df



if __name__ == '__main__':

    # df = pd.read_csv('complete_df_1.csv')
    df = pd.read_csv('complete_df.csv')
    # df.pop('Unnamed: 0')

    # test = 'http://stats.espnscrum.com/statsguru/rugby/match/268591.html?view=scorecard'
    # #
    # test2 = 'http://stats.espnscrum.com/statsguru/rugby/match/95332.html?view=scorecard'
    # #
    # test3 = 'http://stats.espnscrum.com/statsguru/rugby/match/25692.html?view=scorecard'

    # print('### begin script ###\n')
    # match_id, match_details, score, stats, valid = parse_match(test)
    #
    # match_id2, match_details2, score2, stats2, valid2 = parse_match(test2)
    #
    # match_id3, match_details3, score3, stats3, valid3 = parse_match(test3)

    #
    # home, away, short = return_flags(stats)
    #
    # print('### creating row dictionary ###\n')
    # row = create_row_dict(match_id, match_details, score, stats, home, away, short)
    #
    # df = append_row(df, row)
    #
    # print('### complete! ###')

    # match_id_lst = log_page_ids()
    # match_id_lst = [296319, 296320, 296321]
    # match_id_lst = [298567, 296322, 296323, 296324, 298575, 298576] #2018 rugby championship
    match_id_lst = [298756, 295097, 296610, 299414, 299419] # 2018 fall tour

    df_new = hammer_time(df, match_id_lst)

    df_new.to_csv('complete_df.csv', index=False)

    print('#### ALL DONE WOOOWHOOOOOO!!! ####')



#### no data:
# http://stats.espnscrum.com/statsguru/rugby/match/139124.html?view=scorecard
# http://stats.espnscrum.com/statsguru/rugby/match/25713.html?view=scorecard
# http://stats.espnscrum.com/statsguru/rugby/match/279705.html?view=scorecard
# http://stats.espnscrum.com/statsguru/rugby/match/279707.html?view=scorecard
# http://stats.espnscrum.com/statsguru/rugby/match/279709.html?view=scorecard
# http://stats.espnscrum.com/statsguru/rugby/match/289293.html?view=scorecard
# http://stats.espnscrum.com/statsguru/rugby/match/289301.html?view=scorecard
# http://stats.espnscrum.com/statsguru/rugby/match/287069.html?view=scorecard
# http://stats.espnscrum.com/statsguru/rugby/match/287071.html?view=scorecard
# http://stats.espnscrum.com/statsguru/rugby/match/295032.html?view=scorecard
# http://stats.espnscrum.com/statsguru/rugby/match/295078.html?view=scorecard
# http://stats.espnscrum.com/statsguru/rugby/match/295079.html?view=scorecard
