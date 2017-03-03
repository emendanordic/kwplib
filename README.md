# kwplib

## Introduction

This library script is used by other Klocwork utility scripts to connect with
Klocwork servers using the web API

## Usage

Example

```
from kwplib import KwApiCon

t = KwApiCon()
t.set_url("http://xubuntu:8080")
t.set_user("emenda")

vals = {"action" : "builds",
        "project" : "git" }

# perform action "builds" on project git, on Klocwork server at xubuntu:8080
query_response = t.execute_query(vals)
# if response is None, then there was an error
if query_response.response == None:
    print "Error: " + query_response.error_msg
else:
    for i in query_response.response:
        print i
```

## Python version

Currently developed against python v2.7.x (same as comes packaged with klocwork - *kwpython*)
