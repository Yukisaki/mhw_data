# -*- coding: UTF-8 -*-
from urllib import request
import urllib
import requests
import os
import re
import time
from lxml import etree
import json


soubi = []
soubi_list_1 = []
soubi_list_2 = []
soubi_list_3 = []
soubi_list_4 = []
soubi_list_5 = []
zokusei_list = []

def get_detail_soubi_data():
    try:
        hp_url = r'http://mh-world.net/series-armor-mhw.html'
        testurl = r'http://mh-world.net/armor-mhw/series-カガチ.html'
        testurl = r'http://mh-world.net/armor-mhw/series-ディアネロβ.html'
        res = requests.get(hp_url)
        root = etree.HTML(res.text)
        reqlist = root.xpath('//tbody/tr/td/a')
        f2write = open(r'data.txt', 'a', encoding='utf-8')
        for req_item in reqlist:
            req_url = req_item.xpath('@href')[0]
            res_sub = requests.get(req_url)
            if res_sub.status_code == 404:
                print('url: %s failed!' % req_url)
                continue
            root = etree.HTML(res_sub.text)
            table_list = root.xpath("//table[@class='mum']")
            rare_table = root.xpath("//table[@class='txt-c mum']")
            for table in rare_table[0]:
                if len(table) == 8:
                    rare = int(table.xpath('td')[0].text)
            for table in table_list:
                if len(table.xpath('tbody/tr')[0]) == 5:
                    for tr in table.xpath('tbody/tr'):
                        soubi_dict = {'name': None, 'part': None, 'zokusei1': None, 'zokusei2': None, 'lv1': None, 'lv2': None, 'slot': None, 'rare': rare}
                        for td in tr.xpath('td'):
                            index = tr.xpath('td').index(td)
                            if td.text:
                                soubi_dict = get_soubi_dict(index, td.text, soubi_dict, 0)
                                # print(td.text)
                            else:
                                for li in td.xpath('ul/li'):
                                    zoukusei_index = td.xpath('ul/li').index(li)
                                    soubi_dict = get_soubi_dict(index, li.xpath('text()')[0].lstrip('+'), soubi_dict, zoukusei_index, li.xpath('a')[0].text)
                                    # print(li.xpath('a')[0].text, li.xpath('text()')[0])
                        soubi_dict = complete_soubi_dict(soubi_dict)
                        f2write.write(json.dumps(soubi_dict))
                        f2write.write('\n')
            print('url: %s finished!' % req_url)
            time.sleep(0.5)
        f2write.close()
        print('all finished!')
    except Exception as e:
        print(e)


def get_zokusei_data():
    try:
        zokusei_url = r'http://mh-world.net/skill-all-mhw.html'
        res = requests.get(zokusei_url)
        root = etree.HTML(res.text)
        table_list = root.xpath("//table[@class='txt-c mum']")
        f2write = open(r'data_zokusei.txt', 'a', encoding='utf-8')
        for table in table_list:
            a_list = table.xpath('tr/td/a')
            for a_tag in a_list:
                f2write.write(a_tag.text + '\n')
        f2write.close()
        print('all finished!')
    except Exception as e:
        print(e)


def get_soubi_dict(index, value, soubi_dict, zokusei_index=0, zoukusei_name=None):
    if index == 0:
        soubi_dict['part'] = value
    elif index == 1:
        soubi_dict['name'] = value
    elif index == 2:
        soubi_dict['def'] = value
    elif index == 3:
        soubi_dict['slot'] = value
    elif index == 4:
        soubi_dict['zokusei' + str(zokusei_index + 1)] = zoukusei_name
        soubi_dict['lv' + str(zokusei_index + 1)] = int(value)
    return soubi_dict


def complete_soubi_dict(soubi_dict):
    number, (lv1, lv2, lv3) = get_slot_number(soubi_dict['slot'])
    soubi_dict['slot_number'] = number
    soubi_dict['slot_lv'] = {'lv1': lv1, 'lv2': lv2, 'lv3': lv3}
    if soubi_dict['lv2']:
        soubi_dict['total_skill'] = soubi_dict['lv1'] + soubi_dict['lv2']
    else:
        soubi_dict['total_skill'] = soubi_dict['lv1']
    return soubi_dict


def get_slot_number(slot):
    slot_list = slot.split('/')
    number = 3
    lv1 = lv2 = lv3 = 0
    for item in slot_list:
        if item == '-':
            number = number - 1
        elif item == '1':
            lv1 = lv1 + 1
        elif item == '2':
            lv2 = lv2 + 1
        elif item == '3':
            lv3 = lv3 + 1
    return number, (lv1, lv2, lv3)


def get_lv(name, part_dict):
    if part_dict['zokusei1'] and part_dict['zokusei1'] == name:
        return part_dict['lv1']
    elif part_dict['zokusei2'] and part_dict['zokusei2'] == name:
        return part_dict['lv2']
    else:
        return 0

def zokusei_filter(zokusei, soubi_list):
    soubi_list = list(filter(lambda x: x['zokusei1'] == zokusei or x['zokusei2'] == zokusei, soubi_list))
    return soubi_list


def get_filter_soubi_list(filter_keys, soubi_list):
    filter_soubi_list = []
    for key in filter_keys:
        filter_soubi_list = filter_soubi_list + zokusei_filter(key, soubi_list)
    return filter_soubi_list


def get_filter_value(filter_condition_keys, part, filter_values_old):
    filter_values = {}
    for key in filter_condition_keys.keys():
        filter_values[key] = get_lv(key, part)
    if filter_values_old:
        for key in filter_condition_keys.keys():
            filter_values[key] = filter_values_old[key] + filter_values[key]
    return filter_values


def if_satisfied(filter_condition_keys, filter_values):
    flag = True
    for key in filter_condition_keys.keys():
        flag = flag and (filter_values[key] >= filter_condition_keys[key])
    return flag


def zokusei_key_check(filter_condition_keys):
    flag = True
    for key in filter_condition_keys.keys():
        flag = flag and (key in zokusei_list)
    return flag


if __name__ == '__main__':
    # get_detail_soubi_data()
    # get_zokusei_data()

    f2write = open(r'data.txt', 'rU', encoding='utf-8')
    for line in f2write.readlines():
        soubi_dict = json.loads(line)
        if soubi_dict['part'] == '頭':
            soubi_list_1.append(soubi_dict)
        elif soubi_dict['part'] == '胴':
            soubi_list_2.append(soubi_dict)
        elif soubi_dict['part'] == '腕':
            soubi_list_3.append(soubi_dict)
        elif soubi_dict['part'] == '腰':
            soubi_list_4.append(soubi_dict)
        elif soubi_dict['part'] == '脚':
            soubi_list_5.append(soubi_dict)
    f2write.close()

    f2write = open(r'data.txt', 'rU', encoding='utf-8')
    for line in f2write.readlines():
        zokusei_list.append(line)
    f2write.close()

    rare = 4
    soubi_list_1 = list(filter(lambda x: x['rare'] >= rare, soubi_list_1))
    soubi_list_2 = list(filter(lambda x: x['rare'] >= rare, soubi_list_2))
    soubi_list_3 = list(filter(lambda x: x['rare'] >= rare, soubi_list_3))
    soubi_list_4 = list(filter(lambda x: x['rare'] >= rare, soubi_list_4))
    soubi_list_5 = list(filter(lambda x: x['rare'] >= rare, soubi_list_5))

    filter_condition_keys = {u'弱点特効': 2, u'超会心': 1, u'体術': 2, u'回避性能': 1}
    if not zokusei_key_check:
        print('属性存在しない!')
    else:
        filter_soubi_list_1 = get_filter_soubi_list(filter_condition_keys.keys(), soubi_list_1)
        filter_soubi_list_2 = get_filter_soubi_list(filter_condition_keys.keys(), soubi_list_2)
        filter_soubi_list_3 = get_filter_soubi_list(filter_condition_keys.keys(), soubi_list_3)
        filter_soubi_list_4 = get_filter_soubi_list(filter_condition_keys.keys(), soubi_list_4)
        filter_soubi_list_5 = get_filter_soubi_list(filter_condition_keys.keys(), soubi_list_5)
        for item1 in filter_soubi_list_1:
            for item2 in filter_soubi_list_2:
                for item3 in filter_soubi_list_3:
                    for item4 in filter_soubi_list_4:
                        for item5 in filter_soubi_list_5:
                            soubi.append([item1, item2, item3, item4, item5])

        for comb in soubi:
            tokkou = 0
            taijutu = 0
            kaisin = 0
            sutamina = 0
            kaihi = 0
            total_skill_level = 0
            total_lv1_slot = total_lv2_slot = total_lv3_slot = 0
            slot_num = 0
            filter_values = None
            for part in comb:
                total_skill_level = total_skill_level + part['total_skill']
                total_lv1_slot = total_lv1_slot + part['slot_lv']['lv1']
                total_lv2_slot = total_lv2_slot + part['slot_lv']['lv2']
                total_lv3_slot = total_lv3_slot + part['slot_lv']['lv3']
                slot_num = slot_num + part['slot_number']
                # tokkou = tokkou + get_lv(u'弱点特効', part)
                # taijutu = taijutu + get_lv(u'体術', part)
                # kaisin = kaisin + get_lv(u'超会心', part)
                # sutamina = sutamina + get_lv(u'スタミナ急速回復', part)
                # kaihi = kaihi + get_lv(u'回避性能', part)
                filter_values = get_filter_value(filter_condition_keys, part, filter_values)
            # if kaihi >= 5:
            # if tokkou == 3 and kaisin == 1 and taijutu >= 3 and kaihi >= 0:
            if if_satisfied(filter_condition_keys, filter_values):
            # if total_skill_level >= 15:
                soubi_st = ''
                for x in comb:
                    soubi_st = soubi_st + x['name'] + ' ' + x['zokusei1'] + ' lv(' + str(x['lv1']) + ')' + (', ' + x['zokusei2'] + ' lv(' + str(x['lv2']) + ') [' + x['slot'] +  '] / ' if x['zokusei2'] else ' [' + x['slot'] + '] / ')
                print(soubi_st)
                print('slot: %s, total_skill_lv: %s, lv1_slot: %s, lv2_slot: %s, lv3_slot: %s' % (slot_num, total_skill_level, total_lv1_slot, total_lv2_slot, total_lv3_slot))
                print(filter_values)
