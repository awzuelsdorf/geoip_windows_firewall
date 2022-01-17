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

import sys
import argparse
import pandas as pd
import sqlite3
import re
import os
import time

from ip_address_utils import get_ip_cidr_from_ips

DEFAULT_BATCH_SIZE = 500000
DEFAULT_COLUMNS = set(["netname", "mnt-irt", "tech-c", "mnt-routes", "country", "admin-c", "org", "last-modified", "source", "geoloc", "remarks", "mnt-by", "descr", "status", "inetnum", "abuse-c", "language", "mnt-lower", "ip_cidr", "created", "notify", "mnt-domains", "sponsoring-org"])

def save_records(records, columns, sqlite_file_path, csv_file_path):
    df_dict = {column: list() for column in columns}

    for record_i in records:
        # Check for unrecognized column names. Print warning and skip unrecognized columns if there are some.
        unrecognized_columns = set(record_i.keys()).difference(columns)

        if unrecognized_columns:
            sys.stderr.write(f"WARNING: Unrecognized column(s) found in record {record_i}: {', '.join(unrecognized_columns)}\nThese columns will be discarded from this record.\n")

        for column in columns:
            if column in unrecognized_columns:
                continue

            column_value = record_i.get(column)

            if column_value is None:
                df_dict[column].append(None)
            else:
                df_dict[column].append(str(column_value).strip())
 
    df = pd.DataFrame(df_dict)

    database = sqlite_file_path

    if database is not None:
        with sqlite3.connect(database) as conn:
            df.to_sql("Data", con=conn, if_exists='append', index=False)

    csv_file = csv_file_path

    if csv_file is not None:
        df.to_csv(csv_file, mode='a', index=False)

def main():
    start_time = time.time()

    parser = argparse.ArgumentParser(description="Parses information from ICAAN's <zone>.db.inetnum files into a SQLite file, a CSV file, or both.")

    parser.add_argument("-i", "--db-inetnum-file-path", dest="db_inetnum_file_path", required=True, type=argparse.FileType(mode='r', encoding='utf-8', errors='ignore'), help="Path to <zone>.db.inetnum file. Example: C:\\Users\\Admin\\Documents\\apnic.db.inetnum")
    parser.add_argument("-c", "--output-csv-file-path", dest="csv_file_path", default=None, required=False, help="Path to output CSV file. Example: C:\\Users\\Admin\\Documents\\apnic.csv")
    parser.add_argument("-s", "--output-sqlite-file-path", dest="sqlite_file_path", default=None, required=False, help="Path to output SQLite file. Example: C:\\Users\\Admin\\Documents\\apnic.sqlite")
    parser.add_argument("--columns", dest="columns", default=None, required=False, type=str, help=f"Names of columns to include in output, separated by commas. If not provided, will include default columns {', '.join(DEFAULT_COLUMNS)}")
    parser.add_argument("--batch-size", dest="batch_size", default=DEFAULT_BATCH_SIZE, type=int, required=False, help="Number of records to write to SQLite db and/or CSV file in one batch.")

    args = parser.parse_args()

    columns_downselect = set([col.strip() for col in args.columns.split(",")]) if args.columns is not None else None

    if args.csv_file_path is None and args.sqlite_file_path is None:
        parser.error("Neither CSV nor SQLite file path provided. Please provide a SQLite file path, a CSV file path, or both.")

    if args.csv_file_path is not None:
        if os.path.isfile(args.csv_file_path):
            os.remove(args.csv_file_path)

    if args.sqlite_file_path is not None:
        if os.path.isfile(args.sqlite_file_path):
            os.remove(args.sqlite_file_path)

    num_records = 0

    args = parser.parse_args()

    if args.csv_file_path is None and args.sqlite_file_path is None:
        parser.error("Neither CSV nor SQLite file path provided. Please provide a SQLite file path, a CSV file path, or both.")

    df_dict = dict()

    with args.db_inetnum_file_path as inet_file:
        records = list()
        record = dict()

        column_name = None

        for line in inet_file:
            # RIPE NCC uses # and % to indicate comments or other data not
            # used in records, APNIC uses # to indicate comments.
            if line.startswith("#") or line.startswith("%"):
                continue
            # A newline means we've encountered a new record. Assuming the old
            # record has data (the previous section wasn't all comments or other
            # irrelevant data), save off the record. If the old record has no
            # data, then increase the line number and continue.
            elif line.strip() == "":
                if record:
                    records.append(record)
                    record = dict()

                if len(records) == args.batch_size:
                    save_records(records, DEFAULT_COLUMNS if columns_downselect is None else columns_downselect, args.sqlite_file_path, args.csv_file_path)
                    num_records += args.batch_size
                    records = list()
            else:
                line_parts = re.findall(r"^([a-zA-Z0-9\-]+)\:(.*)", line.rstrip())

                if len(line_parts) == 1 and len(line_parts[0]) == 2:
                    column_name = line_parts[0][0]

                    if columns_downselect is not None and column_name not in columns_downselect:
                        continue

                    column_value = line_parts[0][1]

                    if column_name not in record:
                        record[column_name] = column_value
                    else:
                        record[column_name] += f"\n{column_value}"

                    if column_name == "inetnum" and (columns_downselect is None or "ip_cidr" in columns_downselect):
                        if column_value is not None:
                            record["ip_cidr"] = get_ip_cidr_from_ips(column_value.split(" - "))
                        else:
                            record["ip_cidr"] = None
                else:
                    if columns_downselect is None or column_name in columns_downselect:
                        record[column_name] += f"\n{line.rstrip()}"

        if len(records) > 0:
            save_records(records, DEFAULT_COLUMNS if columns_downselect is None else columns_downselect, args.sqlite_file_path, args.csv_file_path)
            num_records += len(records)

    runtime = int(time.time() - start_time)

    print(f"Found {num_records} records in {runtime} seconds (about {num_records / runtime} records per second on average)")

if __name__ == "__main__":
    main()
