#!/usr/bin/python3

# Copyright 2018-2018 Mick Costello.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# -*- coding: utf-8 -*-


import argparse
import requests
import sys

from bs4 import BeautifulSoup


g_tvOnly = False
g_radioOnly = False
g_fullFormat = False


url = "http://en.kingofsat.net/freqs.php?&pos=28.2E&standard=all&ordre=freq&filtre=Clear"


def textValue(col):
    for string in col.stripped_strings:
        if len(string) > 0:
            return '"{}"'.format(string)
    return '""'

def multipleTextValues(col):
    strings = []
    for string in col.stripped_strings:
        strings.append('"{}"'.format(string))
    return strings

def intValue(col):
    for string in col.stripped_strings:
        if string.isdigit():
            return string
    return str(-1)


def saveTransponder(row):

    try:

        cols = row.find_all('td')

        frequency   = str(int(float(cols[2].text.strip())*1000))
        polarity    = textValue(cols[3]).lower()
        standard    = textValue(cols[6])
        modulation  = textValue(cols[7]).lower()
        tmp = multipleTextValues(cols[8])
        symbolRate  = str(int(tmp[0].strip('"'))*1000)
        fec         = tmp[1]
        networkId   = intValue(cols[10])
        transportId = intValue(cols[11])

        if modulation.startswith("16APSK"):
            modulation = "16APSK"

        print('{}, {}, {}, {}, {}, {}, {}, {}'.format(
                transportId,
                networkId,
                frequency,
                symbolRate,
                fec,
                polarity,
                modulation,
                standard))

    except:

        return


def saveChannel(row):

    try:

        cols = row.find_all('td')

        if cols[2].text.strip() == 'Name':
            return

        name      = textValue(cols[2])
        genre     = textValue(cols[4])
        serviceId = intValue(cols[7])
        videoPid  = intValue(cols[8])
        audioPid  = intValue(cols[9])
        pmtPid    = intValue(cols[10])
        pcrPid    = intValue(cols[11])
        txtPid    = intValue(cols[12])

        if videoPid == '-1' and audioPid == '-1':
            return
        if g_tvOnly and videoPid == '-1':
            return
        if g_radioOnly and videoPid != '-1':
            return

        if g_fullFormat:

            print('{:>20}, {:>10}, {:>5}, {:>5}, {:>5}, {:>5}, {:>5}, {:>5}'.format(
                    name,
                    genre,
                    serviceId,
                    videoPid,
                    audioPid,
                    pmtPid,
                    pcrPid,
                    txtPid))

        else: # MythTV

            print('  {:>5}, {:>5}'.format(
                    name,
                    serviceId))

    except:

        return


def main():

    global g_tvOnly, g_radioOnly, g_fullFormat

    parser = argparse.ArgumentParser(description='Scan KingOfSat for TV/Radio channels.')
    parser.add_argument('-t', '--tvOnly', default=False, action='store_true', help='Scan for TV channels only.')
    parser.add_argument('-r', '--radioOnly', default=False, action='store_true', help='Scan for Radio channels only.')
    parser.add_argument('-f', '--fullFormat', default=True, action='store_true', help='Output in full format (include PIDs).')
    args = parser.parse_args()

    g_tvOnly = args.tvOnly
    g_radioOnly = args.radioOnly
    g_fullFormat = args.fullFormat

    print()
    print('# transportId, networkId, frequency, symbolRate, fec, polarity, modulation, standard')
    if g_fullFormat:
        print('# name, genre, serviceId, videoPid, audioPid, pmtPid, pcrPid, txtPid')
    else:
        print('# name, serviceId')

    print()

    page = requests.get(url)
    soup = BeautifulSoup(page.text, "lxml")

    tables = soup.find_all('table', {"class":"frq"})
    for table in tables[1:]:

        transponder = table.find('tr')
        saveTransponder(transponder)

        div = table.find_next_sibling('div')
        channels = div.find_all('tr')
        for channel in channels:
            saveChannel(channel)

        print()

    print()

    return 0


if __name__ == '__main__':

    sys.exit(main())


