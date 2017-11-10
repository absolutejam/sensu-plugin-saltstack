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
    "eauth": "pam",
    "clientmatch": "__name__.mydomain.local"
  }
}
```

### Name matching

Additionally, the handler can substitute the client's name into a string,
allowing it to be altered to match the Salt minion name if it differs. It
achieves this by substituting the salt client `name` attribute into a string,
replacing an instance of `__name__`, allowing for addition of wildcards `*`,
a domain names, prefixs etc. to be passed to the salt run command. For
example, if the salt minion name is `webserver01` but the Salt minion name is
`webserver01.webfarm.local`, you can use `__name__.webfarm.local`.

To substitute this value, the handler will look in 3 places, stopping upon 
the first instance it finds:

- It will first look in the check definition for the `salt_clientmatch` key.
- Next it will look in the client definition for the `salt_clientmatch` key.
- Finally, it will look in the handler configuration for the `clientmatch` key
  with the Salt dictionary.

This allows for granular overriding of the client name property.


### Event data as pillar data

The [event data](https://sensuapp.org/docs/latest/reference/events.html#example-event)
 is available within the `event` pillar, which can be accessed within a `.sls`
 by including the jinja `{{ pillar.get('event') }}`. Please see example usage
 below for more info.

## Example usage

Below is a basic disk check, that will warn on disks being over 80% full and 
alert as critical on 90% usage. As you can see, `salt_sls` key points to
`remediation.disks` which would be equivalent to to the file 
`salt://remediation/disks.sls` on the Salt master.

```
{
  "checks": {
    "disk-free-win": {
      "command": ":::ruby::: C:\\\\opt\\\\sensu\\\\check-scripts\\\\check-windows-disk.rb -w :::vars.disk.warn|80::: -c :::vars.disk.crit|90:::",
      "description": "Checks how full disks are",
      "handlers": [
        "saltstack"
      ],
      "interval": 60,
      "occurrences": 1,
      "refresh": 3600,
      "salt_sls": "remediation.disks",
      "subscribers": [
        "winservers"
      ]
    }
  }
}
```

Within the remediation state file, you could have the following:

```
{% set event = pillar.get('event') %}

{% set temp_dirs = ['C:\\Windows\\Temp', 'C:\\my\\app\\logs'] %}

"Clear files in temp dir {{ temp_dir }}":
  file.directory:
    - name: {{ temp_dir }}
    - clean: True

{% endfor %}

"Send message to Slack":
  slack.post_message:
    - channel: '#autoremediation'
    - from_name: SaltStack
    - message: |
        Disk usage remediation running on *{{ event['client']['name'] }}*
        Sensu reported: {{ event['check']['output'] }}
    - api_key: myapikey
```

And include any other steps, such as restarting services, changing page 
file size, etc.

# TODOs

  [ ] Add timeout when waiting for API
  [ ] Add HTTPS support (with cert checking?)
  [ ] Make the api calls more flexible 
  [x] Pass event data as pillar data
