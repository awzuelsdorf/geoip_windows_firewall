#! /bin/bash

curl -XGET https://ftp.apnic.net/apnic/whois/apnic.db.inetnum.gz -o apnic.db.inetnum.gz
curl -XGET https://ftp.ripe.net/ripe/dbase/split/ripe.db.inetnum.gz -o ripe.db.inetnum.gz

gunzip apnic.db.inetnum.gz
gunzip ripe.db.inetnum.gz

if [ "$(/usr/bin/which virtualenv)" == "" ]; then
    echo "No virtualenv command found. Please install virtualenv and try again.";
    exit 1;
fi

if [ ! -d ".env" ]; then
    echo "No virtualenv .env found. Creating one.";

    if [ "$(/usr/bin/which python3)" != "" ]; then
        virtualenv -p python3 .env;
    else
        virtualenv .env;
    fi

    echo "Activating virtualenv.";

    if [ -f ".env/Scripts/activate" ]; then
        source .env/Scripts/activate;
    elif [ -f ".env/bin/activate" ]; then
        source .env/bin/activate;
    else
        echo "No environment activation found. Please try again.";
        exit 2;
    fi

    echo "Installing requirements to virtualenv.";
    pip install -r requirements.txt;

    echo "Finished creating virtualenv";
    deactivate;
fi

echo "Activating virtualenv."

if [ -f ".env/Scripts/activate" ]; then
    source .env/Scripts/activate;
elif [ -f ".env/bin/activate" ]; then
    source .env/bin/activate;
else
    echo "No environment activation found. Please try again.";
    exit 3;
fi

python inetnum_file_parser.py -i ripe.db.inetnum -c ripe.db.inetnum.csv --batch-size 1000 2>&1 | tee setup_inetnum_ripe_output.log
python inetnum_file_parser.py -i apnic.db.inetnum -c apnic.db.inetnum.csv --batch-size 1000 2>&1 | tee setup_inetnum_apnic_output.log

output_file="consolidated_china_iran_russia_hong_kong_north_korea.txt"

# The US State Department has stated effectively that Hong Kong should be treated as part of Communist China.
# Given this guidance, any firewall rules to block connections from the PRC should most likely apply to Hong
# Kong as well. To exclude Hong Kong from the block list, remove 'HK' from the arguments below.
python consolidate_ips.py -i apnic.db.inetnum.csv,ripe.db.inetnum.csv -c RU,IR,CN,KP,HK -o $output_file