"""
Copyright 2021 Andrew Zuelsdorf
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import ip_address_utils

import pandas as pd
import argparse

def main():
    parser = argparse.ArgumentParser(description="Consolidates IP CIDRs that overlap from different CSV files made by 'inetnum_file_parser.py` into one file with one non-overlapping IP CIDR per line. Allows optional downselection by country code to only consolidate the files' IP CIDRs from certain countries.")

    parser.add_argument('-i', '--input-files', dest="input_files", required=True, help="Input CSV files, names separated by commas, with a column named \"ip_cidr\" that contains IP CIDRs to consolidate and, optionally, a column named \"country\" containing the IP CIDR's host country code. Examples of valid arguments: 1) \"apnic.csv,afnic.csv\" 2) \"apnic.csv\" 3) \"apnic.csv,afnic.csv,other_suspect_countries.csv\"")
    parser.add_argument('-c', '--country-codes', dest="country_codes", required=False, help="Country codes, separated by commas, to use in filtering IP CIDRs. Examples of valid arguments: 1) \"cn,ru\" (People's Republic of China, Russian Federation) 2) \"cn\" (People's Republic of China) 3) \"CN,ir,RU\" (People's Republic of China, Islamic Republic of Iran, Russian Federation)", default=None)
    parser.add_argument('-o', '--output-file', dest="output_file", required=True, help="Output text of consolidated IP CIDRs, one CIDR per line.", type=argparse.FileType(mode='w', encoding='utf-8'))

    args = parser.parse_args()

    country_codes = args.country_codes.split(",") if args.country_codes is not None else []

    # The database can often have multiple casings for a given country code.
    country_codes_cased = []

    for country_code in country_codes:
        country_codes_cased.append(country_code.upper())
        country_codes_cased.append(country_code.lower())

    country_ip_cidrs = list()

    for input_file_path in args.input_files.split(','):
        ip_data = pd.read_csv(input_file_path.strip())

        if country_codes_cased:
            country_ip_cidrs.extend(ip_data.loc[ip_data["country"].isin(country_codes_cased), "ip_cidr"])
        else:
            country_ip_cidrs.extend(ip_data.loc[:, "ip_cidr"])

    print(f"Found {len(country_ip_cidrs)} CIDRs for country codes {', '.join(country_codes_cased)}")

    consolidated_ip_cidrs = ip_address_utils.consolidate_ip_cidrs(country_ip_cidrs)

    print(f"Reduced to {len(consolidated_ip_cidrs)} IP CIDRs from {len(country_ip_cidrs)} original IP CIDRs")

    with args.output_file as consolidated_file:
        for ip_cidr in consolidated_ip_cidrs:
            consolidated_file.write(f"{ip_cidr}\n")

if __name__ == "__main__":
    main()
