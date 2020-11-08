# checkdomain_api_cli.py

Simple script for managing  Records of checkdomain.de NS

Reference:

https://developer.checkdomain.de/reference/v1/domains/%7Bdomain%7D/nameservers/records/

Example usage:

checkdomain_api_cli.py --set-record  --record-name $FQDN --record-type A --record_value $IP --ttl 180 


You will need to add token and domain in the script


This is still in progress, lol
