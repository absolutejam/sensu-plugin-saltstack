# sensu-plugin-saltstack

SaltStack handler for Sensu.

# Overview

*This repo is currently a work-in-progress, as a lot of the Python-based 
plugins for Sensu are new or developing.*

Configuration for the handler is available in `handler_saltstack.json`,
with all fields barring `eauth` being mandatory (Defaults to `auto`).

The handler will look for a `salt_sls` or `salt_orch` key on the check,
which should be the path to the `.sls`, and it will send a request to 
the Salt API to apply the state/run the orchestration at this path
(Uses `foo.bar` notation, not filesystem notation).

## Config

Example config:
```
{
  "handlers": {
    "saltstack": {
      "command": "/etc/sensu/handlers/handler_saltstack.py",
      "type": "pipe"
    }   
  },  
  "saltstack": {
    "username": "saltapiuser",
    "password": "saltapiuser",
    "url": "http://saltstack:8000",
    "eauth": "pam"
  }
}
```

Additionally, the handler can substitute the client's name into a string,
allowing for the addition of wildcards `*`, domain names, etc. in the event
that the Sensu client has a slightly different name to the Salt minion.

It will first look in the check definition for the `salt_clientmatch` key,
which should be something like `{{ name }}.mydomain.local` (Assuming that
your Salt minion name matches the above with `{{ name }}` substituted). If
that isn't defined, it will look for a setting in the handler definition
called `clientmatch`. Finally, it will give up and just use the name from the 
checkk result.


# TODOs

  - Add timeout when waiting for API
  - Add HTTPS support (with cert checking?)
  - Make the api calls more flexible 
