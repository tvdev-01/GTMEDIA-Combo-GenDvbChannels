#!/usr/bin/python3

# Copyright 2021-2021 Mick Costello.
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
import mysql.connector
import os
import sys


DEFAULT_CONFIG_FILE = 'channels.conf'
DEFAULT_CHANNELS_FILE = 'channels'
DEFAULT_TERRESTRIAL_CHANNELS_FILE = 'channels-terrestrial.xml'


g_config = {}
g_nextChannelId = 100


def doLoadConfig(configFile):

    global g_config

    try:

        lineNumber = 0
        with open(configFile) as fi:

            while True:

                line = fi.readline()
                lineNumber = lineNumber + 1

                if not line:
                    break

                config = line.strip()
                if config == '' or config.startswith('#'):
                    continue

                channelNumber, channelName, serviceid, favourites = config.split(',')
                channelNumber = channelNumber.strip()
                channelName = channelName.strip().strip('"')
                serviceId = serviceid.strip()
                favourites = favourites.strip()

                if not serviceId == '':
                    g_config[serviceId] = (channelNumber, channelName, favourites)

    except:

        print("Syntax error on line {}".format(lineNumber))
        print("({})".format(line))
        sys.exit(-1)


def processTransponder(transponder, fi):

    global g_nextChannelId

    transportId, networkId, frequency, symbolRate, fec, polarity, modulation, standard = transponder.split(',')
    transportId = transportId.strip()
    networkId = networkId.strip()
    frequency = frequency.strip()
    symbolRate = symbolRate.strip()
    fec = fec.strip().strip('"')
    polarity = polarity.strip().strip('"').upper()
    modulation = modulation.strip().strip('"')
    standard = standard.strip().strip('"')

    print('''        <transponder original_network_id="{}"
                ts_id="{}"
                frequency="{}"
                symbol_rate="{}"
                polarisation="{}"
                sub_sys="0">'''.format(networkId,transportId,frequency,symbolRate,polarity))

    while True:

        channel = fi.readline().strip()
        if not channel:
            break

        name, genre, serviceId, videoPid, audioPid, pmtPid, pcrPid, txtPid = channel.split(',')
        name = name.strip().strip('"')
        genre = genre.strip().strip('"')
        serviceId = serviceId.strip()
        videoPid = videoPid.strip().strip('"')
        audioPid = audioPid.strip().strip('"')
        pmtPid = pmtPid.strip().strip('"')
        pcrPid = pcrPid.strip().strip('"')
        txtPid = txtPid.strip().strip('"')

        if serviceId in g_config.keys():

            lcn = g_config[serviceId][0]
            if g_config[serviceId][1]:
                name = g_config[serviceId][1]

            serviceType = 1 # TV
            if int(g_config[serviceId][0]) > 1000:
                serviceType = 2 # Radio

            favourites = g_config[serviceId][2]

            print('''            <program name="xxx{}"
                    service_id="{}"
                    channel_number="{}"
                    type="{}"
                    scrambled="false"
                    parental_lock="false"
                    skip="false"
                    id="{}"
                    pmt_pid="{}"
                    plp_id="256"
                    default_channnel_num="{}"
                    lcn="{}"
                    fav="{}">'''.format(name, serviceId, lcn, serviceType, g_nextChannelId, pmtPid, lcn, lcn, favourites))

            print('                <video pid="{}"/>'.format(videoPid))
            print('                <pcr pid="{}"/>'.format(pcrPid))
            print('                <audio pid="{}" language="eng"/>'.format(audioPid))

            print('            </program>')

            g_nextChannelId = g_nextChannelId + 1

    print('''        </transponder>
    ''')


def main():

    parser = argparse.ArgumentParser(description='Generate GTMEDIA database.')
    parser.add_argument('--config-file', default=DEFAULT_CONFIG_FILE, type=str, help='Config filename.')
    parser.add_argument('--channels-file', default=DEFAULT_CHANNELS_FILE, type=str, help='Channels filename.')
    parser.add_argument('--terrestrial-channels-file', default=DEFAULT_TERRESTRIAL_CHANNELS_FILE, type=str, help='Terrestrial channels filename.')
    args = parser.parse_args()

    config_file = args.config_file
    channels_file = args.channels_file
    terrestrial_channels_file = args.terrestrial_channels_file

    doLoadConfig(config_file)

    print('<?xml version="1.0" encoding="utf-8"?>')

    print('''<db>
    ''')

    print('''    <version winsat_editer="30"/>
    ''')

    print('''    <satellite
            name="Universal"
            selected="1"
            local_longitude="0 E"
            local_latitude="0 N"
            sat_longitude="282 E"
            lof_hi="10600000"
            lof_lo="9750000"
            lof_threshold="11700000"
            lnb_power="on 13/18v"
            signal_22khz="off"
            toneburst="none"
            diseqc1_0="none"
            diseqc1_1="none"
            motor="none"
            position="0">
            ''')

    with open(channels_file) as fi:
        while True:

            line = fi.readline()
            if not line:
                break

            transponder = line.strip()
            if transponder == "" or transponder.startswith('#'):
                continue

            processTransponder(transponder, fi)

    print('''    </satellite>
    ''')

    if os.path.exists(terrestrial_channels_file):
        with open(terrestrial_channels_file) as fi:
            while True:

                line = fi.readline()
                if not line:
                    break

                print(line.rstrip())

    print('''</db>
    ''')

    return 0


if __name__ == '__main__':

    sys.exit(main())

