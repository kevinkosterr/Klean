# Getting started

[TOC]

## Installation
Installing the package is easily done via `uv` or `pip`.
```bash
uv add klean-cli
```
or
```bash
pip install klean-cli
```

## Usage
```bash
klean {filesystem} [OPTIONS]
```
Available filesystems:
<ul>
    <li><code>local</code> - MacOS, Linux, Windows (included)</li>
</ul>
!!! note "Installing Filesystems"
    Other filesystems can be installed as plugins e.g. [klean-b2-plugin](https://github.com/kevinkosterr/klean-b2-plugin).
    See a full list of official plugins [here](/plugins).

Available options:
<ul>
    <li><code>--help</code>: Show the help message;</li>
    <li><code>--no-dry-run</code>: Disable dry run mode (on by default);</li>
    <li><code>--verbose</code>: Enable verbose output.</li>
</ul>


