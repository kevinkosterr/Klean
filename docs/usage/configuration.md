# Configuration setup
This is a guide to setting up Klean's configuration options. The configuration file is in the `toml` format.
And is located at `~/<user>/.config/klean/config.toml`.

## Options walkthrough

### Main section
The main section defines all primary configuration options for Klean. This mainly has to do with parsing filenames to
dates and parsing database names from the filenames.

<h4 id="prefix" data-toc-label="prefix">
prefix <span class="badge info">str</span> <span class="badge">optional</span>
</h4>
> The prefix is used to separate the date from the rest of the filename. E.g. in "klean+2019-01-01", the prefix would be
either `+` to have `klean` as the database name, or `klean+`.

<h4 id="suffix" data-toc-label="suffix">
suffix <span class="badge info">str</span> <span class="badge">optional</span>
</h4>
> The suffix is used to separate the date from the rest of the filename. E.g. in "klean+2019-01-01.tar.gz", the suffix would be `.`.

<h4 id="datetime_format" data-toc-label="datetime_format">
datetime_format <span class="badge info">str</span> <span class="badge required">required</span>
</h4>
> A format string for parsing dates from filenames. Must be compatible with Python's `datetime.strptime` function.

<h4 id="date_format" data-toc-label="date_format">
date_format <span class="badge info">str</span> <span class="badge">optional</span>
</h4>
> Alias for `datetime_format`

<h4 id="replace_extra" data-toc-label="replace_extra">
replace_extra <span class="badge info">List[str]</span> <span class="badge">optional</span>
</h4>
> A list of extra characters to replace by a blank string in filenames.

### Bucket sections
Bucket sections in the `config.toml` file are special sections within the configuration file that are used to define
the buckets that Klean will use to group data and decide which files to delete.

!!! important "IMPORTANT"
    Order of definition is very important here, naming is not relevant. Klean will take the first bucket section it finds
    and use that as the first bucket, the second one as the second bucket and so on.

#### Bucket options
Each bucket section has the following options:
<ul>
    <li><code>hours_between</code> <span class="badge">optional</span> - The maximum amount of hours between each bucket. 
        It is recommended to add .5 hours to your maximum amount of hours as a failsafe. If not defined</li>
    <li><code>period_in_days</code> <span class="badge required">required</span> - Determines in which timeframe the
    bucket exists, so 7 is within a week from the first file Klean comes across.</li>
</ul>

#### Defining a bucket section
You can define a new bucket section like so:
```toml
[bucket_one] # Example name, you can use anything here
# hours_between is not defined here, because we don't want any files to be deleted inside this bucket.
period_in_days = 7 # determines in which timeframe the bucket exists, so 7 is within a week from the first file Klean comes across.

[bucket_two]
hours_between = 4.5
period_in_days = 14
```
