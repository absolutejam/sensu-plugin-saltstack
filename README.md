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

# TODOs

  - Add timeout when waiting for API
  - Add HTTPS support (with cert checking?)
  - Make the api calls more flexible 
