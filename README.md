# Klean

> A database backup cleaner. Sorts files by date and deletes the ones you don't need anymore. 

![GitHub top language](https://img.shields.io/github/languages/top/kevinkosterr/Klean)

Klean gets the filenames out of your Local Drive or BackBlaze, sorts them by the date given inside the filename. 
Klean works with buckets, each bucket represents a period of days given inside the ` config.toml` file 
(e.g. bucket1 = 14days, bucket2 = 28 days etc).

After sorting the filenames the filenames will be put inside buckets and the difference between each backup is calculated.
If the difference between each backup reaches the maximum allowed amount (given in `config.toml`), it puts all the filenames
between each maximum inside a kill list. Klean will then start getting each filename out of the kill list and deletes 
the files with the same filename.

#### Supports:
<img src="https://github.com/kevinkosterr/Klean/assets/33180770/edf23425-eab4-434d-9352-59d2055b8ec8" style="width: 250px;">


<br>

### Usage:

```bash
python run.py {b2,local} [-v] [--do-delete]
```

`b2` - uses the BackBlaze Cloud Storage (B2FS)

`local` - uses the Local storage (LocalFS)

`-v` - passing this into the command line will enable verbose mode

`--do-delete` - this argument is required, else it will not delete files.

Everything needs to be configured in the `config.toml` file. A full example can be found in the `data` folder. 

### Adding a bucket
Even though the default example shows five buckets, you can always add more yourself. You can do so by specifying any 
key starting with `bucket`. Like so:

```toml
[bucket_six]
hours_between=200
period_in_days=90
```

The name of your bucket isn't all that important, as long as you keep these two things in mind:
- Names of buckets **must** start with 'bucket';
- The order as specified in the `config.toml` file will be the order in which the buckets will be sorted and filled.

### Supported format
Currently Klean only supports the following format of filenames:
```
 [name][prefix]["%Y-%m-%d%" "H:%M:%S"].[file extension]
```

