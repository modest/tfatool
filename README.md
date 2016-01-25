# tfatool: *T*oshiba *F*lash*A*ir Tool

This package provides easy access to
Toshiba's FlashAir wireless SD card. As a library, this project provides
a simple abstraction of the FlashAir API. As a set of scripts, `tfatool`
gives the user a way of synchronizing files and configuring the device
from the command line.

Some motivational command line examples:

  Action                                                      | Command                                         
  ----------------------------------------------------------- | ------------------------------------------------
  Watch FlashAir for new JPEGs, sync to local dir forever     | `flashair-util -s -d /home/tad/Photos --only-jpeg`
  Sync the 10 most recent files with a local dir, then quit   | `flashair-util -S time -d images/new/`  
  Sync files created between Jan 23rd and Jan 26th            | `flashair-util -S all -t 2016-01-23 -T 2016-01-26`
  Sync the five most recent RAW files of a certain name       | `flashair-util -S time -k 'IMG-08.+\.raw'`      
  Change FlashAir network SSID                                | `flashair-config --wifi-ssid myflashairnetwork`
  Show FlashAir network password & firmware version           | `flashair-config --show-wifi-key --show-fw-version`

<img align="right" src="_docs/flashair.jpg">

Features include:

* `flashair-util`: a command line tool for syncing, copying, listing files on FlashAir
* `flashair-config`: a command line tool for configuring FlashAir
* `tfatool.command`: abstraction of FlashAir's [command.cgi](https://flashair-developers.com/en/documents/api/commandcgi/)
* `tfatool.config`: abstraction of FlashAir's [config.cgi](https://flashair-developers.com/en/documents/api/configcgi/)
* `tfatool.sync`: functions to facilitate copying/syncing files from FlashAir

Read the [FlashAir documentation](https://flashair-developers.com/en/documents/api/)
for more information about the API `tfatool` takes advantage of.

# Usage
## Using the `flashair-util` script
### Help menu
```
$ flashair-util -h
usage: flashair-util [-h] [-l] [-c] [-s] [-S {time,name,all}] [-r REMOTE_DIR]
                     [-d LOCAL_DIR] [-j] [-n N_FILES] [-k MATCH_REGEX]
                     [-t EARLIEST_DATE] [-T LATEST_DATE]

optional arguments:
  -h, --help            show this help message and exit

Actions:
  -l, --list-files
  -c, --count-files
  -s, --sync-forever    watch for new files in REMOTE_DIR, copy them to
                        LOCAL_DIR (runs until CTRL-C)
  -S {time,name,all}, --sync-once {time,name,all}
                        move files (all or by most recent name/timestamp) from
                        REMOTE_DIR to LOCAL_DIR, then quit

Setup:
  -r REMOTE_DIR, --remote-dir REMOTE_DIR
                        FlashAir directory to work with (default:
                        /DCIM/100__TSB)
  -d LOCAL_DIR, --local-dir LOCAL_DIR
                        local directory to work with (default: working dir)

File filters:
  -j, --only-jpg        filter for only JPEG files
  -n N_FILES, --n-files N_FILES
                        Number of files to move in --sync-once mode
  -k MATCH_REGEX, --match-regex MATCH_REGEX
                        filter for files that match the given pattern
  -t EARLIEST_DATE, --earliest-date EARLIEST_DATE
                        work on only files AFTER datetime similar to YYYY-MM-
                        DD HH:SS
  -T LATEST_DATE, --latest-date LATEST_DATE
                        work on only files BEFORE datetime similar to YYYY-MM-
                        DD HH:SS

```

### Example 1: sync newly created files on FlashAir card
Watch for new files on the FlashAir SD card. When new files are found,
write them to a specified local directory.

```
$ flashair-util -s -d path/to/files --only-jpg
2016-01-22 21:29:12,336 | INFO | __main__ | Syncing files from /DCIM/100__TSB to path/to/files
2016-01-22 21:28:44,035 | INFO | __main__ | Creating directory 'path/to/files'
2016-01-22 21:29:12,337 | INFO | __main__ | Waiting for newly arrived files...
2016-01-22 21:29:27,412 | INFO | tfatool.sync | Ready to sync new files (39 existing files ignored)
```

Some time later, a new photo appears in the default remote directory.

```
2016-01-22 21:30:05,770 | INFO | tfatool.sync | Files to sync:
  IMG_0802.JPG
2016-01-22 21:30:05,770 | INFO | tfatool.sync | Copying remote file IMG_0802.JPG to stuff/IMG_0802.JPG
2016-01-22 21:30:05,771 | INFO | tfatool.sync | Requesting file: http://flashair/DCIM/100__TSB/IMG_0802.JPG
2016-01-22 21:30:05,866 | INFO | tfatool.sync | Wrote IMG_0802.JPG in 1.00 s (4.31 MB, 4.31 MB/s)
```

### Example 2: sync subset of files on FlashAir *just once*

Sync JPEG files that were created between December 15th, 2015 (at 3:00 pm)
and January 12, 2016 with the local `stuff/` directory.
Notice that *files which already exist and match the size in bytes of those on FlashAir*
are not overwritten.

```
flashair-util -S all -d stuff/ -j -t '2015-12-15 15:00' -T 2016-01-12
2016-01-22 22:29:02,228 | INFO | __main__ | Syncing files from /DCIM/100__TSB to stuff/
2016-01-22 22:29:02,229 | INFO | __main__ | Retreiving ALL matched files
2016-01-22 22:29:02,330 | INFO | tfatool.sync | File 'stuff/IMG_0800.JPG' already exists; not syncing from SD card
2016-01-22 22:29:02,331 | INFO | tfatool.sync | Copying remote file IMG_0801.JPG to stuff/IMG_0801.JPG
2016-01-22 22:29:02,331 | INFO | tfatool.sync | Requesting file: http://flashair/DCIM/100__TSB/IMG_0801.JPG
2016-01-22 22:29:17,831 | INFO | tfatool.sync | Wrote IMG_0801.JPG in 9.40 s (4.31 MB, 0.46 MB/s)
2016-01-22 22:29:17,833 | INFO | tfatool.sync | File 'stuff/IMG_0802.JPG' already exists; not syncing from SD card
2016-01-22 22:29:17,833 | INFO | tfatool.sync | Copying remote file IMG_0803.JPG to stuff/IMG_0803.JPG
2016-01-22 22:29:17,834 | INFO | tfatool.sync | Requesting file: http://flashair/DCIM/100__TSB/IMG_0803.JPG
2016-01-22 22:29:30,855 | INFO | tfatool.sync | Wrote IMG_0803.JPG in 10.07 s (4.55 MB, 0.45 MB/s)
``` 

Other simple `--sync-once` examples include:

* Just grab the most recent JPEG: `flashair-util -S time -n 1`
* Sync most recent 5 files by timestamp: `flashair-util -S time --n-files 5`
* Of all files that end in `08.JPG`, sync the 10 
  greatest filenames: `flashair-util -S name --n-files 10 -k '.+08\.JPG'`


### Example 3: listing certain files on FlashAir

List ALL files:

```
$ flashair-util -l
Files in /DCIM/100__TSB
=======================
IMG_0894.JPG  2016-01-23  16:27:12  3.86MB
IMG_0894.CR2  2016-01-23  16:27:14  17.73MB
...
IMG_0914.JPG  2016-01-23  18:19:58  1.07MB
IMG_0914.CR2  2016-01-23  18:20:00  15.53MB
(249 files, 2.84 GB total)
```

List only JPEGs created on the 16th and 17th of January:

```
& flashair-util -l -t 2016-01-16 -T 2016-01-18 --only-jpg
Files in /DCIM/100__TSB
=======================
IMG_0568.JPG  2016-01-16  18:09:50  4.96MB
IMG_0580.JPG  2016-01-16  18:26:10  5.59MB
IMG_0583.JPG  2016-01-16  18:27:02  5.16MB
IMG_0584.JPG  2016-01-16  18:27:18  5.12MB
IMG_0590.JPG  2016-01-16  20:01:52  5.51MB
IMG_0597.JPG  2016-01-16  21:53:50  4.64MB
IMG_0617.JPG  2016-01-17  00:15:24  5.55MB
(7 files, 36.54 MB total)
```

List JPEGs that match a certain filename pattern:

```
$ flashair-util -l -k 'IMG_058.+' --only-jpg

Files in /DCIM/100__TSB
=======================
IMG_0580.JPG  2016-01-16  18:26:10  5.59MB
IMG_0583.JPG  2016-01-16  18:27:02  5.16MB
IMG_0584.JPG  2016-01-16  18:27:18  5.12MB
(3 files, 15.87 MB total)
```

## Using the `flashair-config` script
### Help menu

```
flashair-config -h
usage: flashair-config [-h] [-m MASTERCODE] [-v] [-t WIFI_TIMEOUT]
                       [-w {access_point,station,passthrough}] [-W]
                       [-k WIFI_KEY] [-K PASSTHROUGH_KEY] [-s WIFI_SSID]
                       [-S PASSTHROUGH_SSID] [--app-info APP_INFO]
                       [--bootscreen-path BOOTSCREEN_PATH] [-M]
                       [--timezone TIMEZONE] [-d {disable,enable,upload}]
                       [--show-wifi-ssid] [--show-wifi-key] [--show-mac]
                       [--show-fw-version] [--show-wifi-mode]

optional arguments:
  -h, --help            show this help message and exit
  -m MASTERCODE, --mastercode MASTERCODE
                        12-digit hex mastercode to enable configuration of the
                        FlashAir device
  -v, --verbose

WiFi settings:
  -t WIFI_TIMEOUT, --wifi-timeout WIFI_TIMEOUT
                        set WiFi timeout of device
  -w {access_point,station,passthrough}, --wifi-mode {access_point,station,passthrough}
                        set WiFi mode of device
  -W, --wifi-mode-on-boot
                        set the WiFi mode on next boot, not immediately
  -k WIFI_KEY, --wifi-key WIFI_KEY
                        set WiFi security key
  -K PASSTHROUGH_KEY, --passthrough-key PASSTHROUGH_KEY
                        set internet passthrough security key
  -s WIFI_SSID, --wifi-ssid WIFI_SSID
                        set WiFi SSID
  -S PASSTHROUGH_SSID, --passthrough-ssid PASSTHROUGH_SSID
                        set internet passthrough SSID

Misc settings:
  --app-info APP_INFO   set application-specific info
  --bootscreen-path BOOTSCREEN_PATH
                        set path to boot screen image
  -M, --clear-mastercode
  --timezone TIMEZONE   set timezone in hours offset (e.g. -8)
  -d {disable,enable,upload}, --drive-mode {disable,enable,upload}
                        set WebDAV drive mode

Show configuration parameters:
  --show-wifi-ssid
  --show-wifi-key
  --show-mac
  --show-fw-version
  --show-wifi-mode
```

### Sample configurations of FlashAir

Set the FlashAir WiFi network's SSID and password.

```flashair-config -k supersecretekey -s myflashairnetwork```

Prepare for Internet passthrough mode. This sets the LAN SSID, password, and
the FlashAir WiFi mode. If this is successful, the device will pass through
Internet access to all connected clients.

```flashair-config -K supersecretekey -S coffeeshopssid -w passthrough```

Set the WiFi mode *on boot* instead of immediately with the *-W* flag:

```flashair-config -w station -W```


## Using the `tfatool` Python library
### Example 1: using FlashAir's command.cgi

```python
from tfatool import command

# get files in a FlashAir directory as a list of namedtuples
# each namedtuple has six attributes: directory, filename, time, date, etc
flashair_files = command.list_files()  # list files in /DCIM/100__TSB by default
special_files = command.list_files(DIR="/DCIM/my_special_folder")

# get an integer count of files in a certain dir
n_flashair_files = command.count_files(DIR="/DCIM")  # count in specific directory


# file list fn takes optional filters
# here we cull any RAW files (.raw or .cr2) and files of a certain name
# you can combine any number of filters
filter_raw = lambda f: not f.filename.lower().endswith(".raw", ".cr2")
filter_name = lambda f: f.filename.lower()startswith("IMG_08")
filter_date = lambda f: f.date > 33002  # look at FlashAir docs for date encoding
certain_files = command.list_files(filter_raw, filter_name, filter_date)

for f in certain_files:
    print("{:s}: {:0.2f} MB".format(f.filename, f.size / 10**6))
```

### Example 2: using file synchronization functions

```python
from tfatool import sync

# Sync files as a one-off action
# here we sync the most recent files sorted by (file.date, file.time)
sync.by_time(count=10)  # places most recent files in CWD by default
sync.by_time(count=15, dest="/home/tad/Pictures")

# Sync specific files selected from files list
from tfatool import command
all_files = command.list_files()
only_camille_photos = [f for f in all_files if "camille" in f.filename.lower()]
sync.by_files(only_camille_photos, dest="/home/tad/Pictures/camille")
```

### Example 3: watching for newly created files

The `tfatool.sync.by_new_arrivals()` function watches your FlashAir device
for new files. When new files are found, they're copied to the local directory
specified by the `dest` argument (current working directory by default).

```python
from tfatool import sync

# Monitor FlashAir for new files, sync them with a local directory
# This will run forever
sync.by_new_arrivals(dest="/home/tad/Pictures/new")

# Sync only .raw image files that are smaller than 3 MB
# This will run forever
is_raw = lambda f: f.filename.lower().endswith(".raw", ".cr2")
is_small = lambda f: f.size < 3e6
sync.by_new_arrivals(is_raw, is_small, dest="/home/tad/Pictures/raw")
```

### Example 4: sending config changes via a POST to *config.cgi*

```python
from tfatool.config import post, config
from tfatool.info import Config

params = {
    Config.app_info: "special application info",
    Config.wifi_timeout: 3600,  # one-hour WiFi timeout
    Config.wifi_ssid: "SUPER FUN PHOTO ZONE",
    Config.timezone: -11,  # somewhere in the USA, for example
}

# This will raise an assertion error if any parameters are invalid
# or out of range (for example if the WiFi timeout is < 60 seconds)
prepped_params = config(params)

# Prompt reconfiguration of the device via an HTTP POST to config.cgi
response = post(prepped_params)
if response.status_code == 200:
    print("FlashAir reconfiguration successful")
else:
    print("Error: {}".format(response.status_code))
```

# Installation
Requires `requests`, `tqdm`, and `python3.4+`. Install with `pip3 install tfatool`.
