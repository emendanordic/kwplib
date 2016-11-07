# kwplib

## Introduction

This library script is used by other Klocwork utility scripts to connect with
Klocwork servers using the web API

## Usage

Example

```
from kwplib import KwApiCon

kwapiconf = KwApiCon()
kwapiconf.set_url("http://localhost:8080")
kwapiconf.set_user("emenda")

vals = {"action" : "builds",
        "project" : "git" }

# perform action "builds" on project git, on Klocwork server at localhost:8080
kwapiconf.execute_query(vals)
```

## Python version

Currently developed against python v2.7.x (same as comes packaged with klocwork - *kwpython*)
