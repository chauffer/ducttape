# ducttape

A health-check service that runs a command when some HTTP conditions are met
(status code, substr)

## Configuration
The only supported way to run this is through Docker, it'll work otherwise,
but you are on your own as to how to do this.

For your convenience, `docker` and `curl` are available in the image.

### Environment variables:
#### Mandatory
  - `DUCTTAPE_URL` - Target URL
  - `DUCTTAPE_RESTART_CMD` - Command to run when conditions are met

### Extra Configuration
  - `DUCTTAPE_MATCH` - Set to a regex if you want to match substr
  - `DUCTTAPE_INTERVAL` - How often it should check
  - `DUCTTAPE_ATTEMPTS` - After how many failures we should run the RESTART_CMD
  - `DUCTTAPE_RESTART_INTERVAL` - How long we should sleep before checking again
  - `DUCTTAPE_REQUESTS_TIMEOUT` - `requests` timeout for the target URL
  - `DUCTTAPE_SLACK_WEBHOOK` - Slack wehbook URL, posts message each restart
  - `DUCTTAPE_SLACK_CHANNEL` - Channel to post to, defaults to webhook default
