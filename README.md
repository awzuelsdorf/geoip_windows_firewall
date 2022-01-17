#GeoIP Windows Firewall#

This repo allows one to create a SQLite database and CSV file of IP address ranges for countries in APNIC and use that database to identify a minimal set of IP CIDRs that can be used to block connections from certain countries that do not need inbound or outbound access to or from the user's Windows PC. It also enables one to update or create firewall rules to block connections from the given countries.

##Acknowledgements##

Thanks to [Jason Fossen](https://www.sans.org/profiles/jason-fossen/) for developing the Import-FirewallBlocklist.ps1 script. 

##Generating the Firewall CIDRs##

You can run `./create_ip_cidrs.sh` on a system that has `curl`, `which`, `python`, and `virtualenv` available to generate the `consolidated_china_iran_russian_hong_kong_north_korea.txt` file that you can use as input for `Import-FirewallBlocklist.ps1`. If you are using Git for Windows and a version of python that is at least 3.6.8, you should already have what you need. This shell script will also generate the two CSVs that are needed to generate the list of consolidated IP CIDRs.

Once you have generated `consolidated_china_iran_russian_hong_kong_north_korea.txt`, please refer to the 'Apply Firewall Rules' section to apply the firewall rules.

##Apply Firewall Rules##
- The `Import-FirewallBlocklist.ps1` script requires Powershell version 3 to be installed.
- In a Powershell shell with administrator privileges:
  - Make note of your current user's execution policies using `Get-ExecutionPolicy -Scope CurrentUser`
  - Run `Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser`
  - Run `.\Import-FirewallBlocklist.ps1 -inputfile .\consolidated_china_iran_russian_hong_kong_north_korea.txt`

None of these commands should have errors. If they do, please resolve them and re-run the commands before continuing.

##Verification##
- Open a command prompt or terminal and run `ping weibo.com` and `ping xinhuanet.com`. You should receive a 'General failure' response from these commands.
- Open a command prompt or terminal and run `ping whitehouse.gov` and `ping weather.gov`. You should receive a response other than 'General failure' from these commands.

If you get an unintended result from pinging these websites, please ensure that your commands finished without errors. If you're still having issues, please open an issue with a short screen recording or link to a YouTube video where you go through the `Apply Firewall Rules` section and run the ping commands for these four websites. Please *do not* submit screenshots or other media or attempt to submit an issue without a recording that goes through all parts of the application and verification processes.

##Licensing##

Apache License 2.0
