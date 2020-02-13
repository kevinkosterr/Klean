# <img src='https://image.flaticon.com/icons/svg/660/660478.svg' width="30" height="30"> Klean

> A database backup cleaner. Sorts files by date and deletes the ones you don't need anymore. 

![version](https://img.shields.io/github/v/release/kevinkosterr/Klean?include_prereleases)

#### supports:

![BackBlaze](https://www.backblaze.com/pics/backblaze-logo.gif)
<br>

### Usage:

```bash
run.py {b2,local} [-y] [--do-delete]
```

`b2` - uses the BackBlaze Cloud Storage(B2FS)

`local` - uses the Local storage(LocalFS)

`-y` - passing this into the command line skips any confirmation

`--do-delete` - this arguments is required, else it will not delete files.

everything is configured in the `config.toml` file. which looks like this by default:

```toml
[main]
#the prefix used in the filenames
#this is used to serperate the databasename and the date that's parsed within
#the filename
prefix = "+"

[LocalFS]
# please enter the full path to the directory
directory = ""

[B2Blaze]
#bucket is the name of the bucket
bucket = ""
#a key_id is required to run this application, you can obtain one in the B2 portal
key_id = ""
#an app_id is required to run this application, you can obtain one in the B2 portal
#your app_id is only shown once
app_id = ""


# 0.5 addition to hours_between is for safety purposes, so the script doesn't accidentally delete wrong files.
[bucket_first]
#by default hours_between isn't defined here, because no
#files should be deleted in the first week

#hours_between=
period_in_days= 7

[bucket_second]
hours_between= 4.5
period_in_days= 14

[bucket_third]
hours_between= 12.5
period_in_days= 28

[bucket_fourth]
hours_between= 24.5
period_in_days= 84

[bucket_fifth]
hours_between= 168.5
period_in_days= 84
```

