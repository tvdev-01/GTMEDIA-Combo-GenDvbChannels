# Generate GTMEDIA Combo (4K) Database

The included python scripts may be used to generate a channels database
for a GTMEDIA Combo (4K) set top box. The output may be compatable with other
GTMEDIA devices but have not been tested.

Satellite channels are generated from latest KingOfSat tables.\
A list of terrestrial channels file may be included if required.

As configure, scripts will generate a sorted subset of channels for Astra 28.2E
with selection of Irish terrestrial channels but may be configuted for other satellites by changing URL in `scanForChannels.py` (line 33).

**CAUTION: Never run untrusted scripts on your PC.**

## Procedure

These scripts are intended to be run from a Mac or Linux command line but can be run on any device which supports Python.

1. Backup your existing database.\
   The import will remove all unnecessary satellite configurations.

2. Create a `channels.conf` using the included file as a template.\
   There are 4 entries for each channel.
   * ***channel number***      - User specified, used for sorting.
   * ***channel name***        - User specified, if blank name from KingOfSat will be used.
   * ***channel service id***  - Get from channel entry in KingOfSat.
   * ***favourities mask***    - User specified, see sample `channels.conf` file.

   <br>Note: Radio channels should be numbered from 1000.

3. If required, create a terristrial channels file. The easiest way to do this is to copy from your backup. See included `channels-terrestrial.xml`.

4. Get an up to date list of channels from KingOfSat
    ```
    ./scanForChannels.py > channels
    ```
5. Generate GTMEDIA database
    ```
    ./genDvbChannels.py > dvbchannel_v30_db.xml
    ```
6. Copy to USB and import into your GTMEDIA device.

Steps 4 to 6 may be repeated as required.


