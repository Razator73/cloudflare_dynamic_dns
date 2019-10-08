# pyflare
Updates Cloudflare with current IP

I didn't want to pay my ISP an extra $5 a month to keep my IP static.
Cloudflare will host your DNS for free, on top of a whole heap of other benefits, and they 
have a really good API for updating DNS records. The idea is that you run this script like 
you would a dynamic DNS client - it's python so entirely cross platform and uses minimal and 
very common libraries.

# Credential file

You will need to create a `cloadflare.json` file in a `~/.creds/` folder - this file must be json formatted 
and contain the following 4 elements. Note the curly braces are not to be included.
```
{
	"key": "{your API key for Cloudflare}",
	"zone_id": "{the DNS zone that contains the record you are updating}"
}
```
