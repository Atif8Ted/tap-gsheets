#!/usr/bin/env python3

import singer
from tap_gsheets.gsheet_loader import GSheetsLoader
import json
from pyhocon import ConfigFactory
from inflection import parameterize, tableize, underscore
import argparse

LOGGER = singer.get_logger()


def sync(config):
    LOGGER.info("Config:", config)

    """
    Authenticates a connection with the Google API, retrieves a spreadsheet and
    outputs its values in a JSON format
    """

    # read config
    sheets = []
    # if "spreadsheet_id" in config:
    #     # one-sheet single page config
    #     sheet = {"spreadsheet_id": config["spreadsheet_id"]}
    #     sheets.append(sheet)
    # else:
    #     sheets = config["sheets"]
    spreadsheets = config["spreadsheets"]
    gsheets_loader = GSheetsLoader(config)

    for spread_sheet in spreadsheets:

        spreadsheet_id = spread_sheet["spreadsheet_id"]

        if "sheets" in spread_sheet:
            worksheets = spread_sheet["sheets"]
        else:
            worksheets = []

        # noinspection PyBroadException
        try:
            if len(worksheets) > 0:
                for worksheet in worksheets:
                    process_worksheet(gsheets_loader, spreadsheet_id, worksheet, config)
            else:
                process_worksheet(gsheets_loader, spreadsheet_id, None, config)
        except Exception as e:
            LOGGER.error(
                f"Can't process a worksheet {spreadsheet_id} because of:\n{e}",
            )
            raise Exception(f"Can't process a worksheet {spreadsheet_id} because of:\n{e}")


def process_worksheet(gsheets_loader, sheet_name, worksheet, config):
    LOGGER.info("Processing worksheet: %s %s", sheet_name, worksheet)
    # if type(sheet_name) is dict:
    #     sheet_name = sheet_name.values()[0]
    if worksheet is None:
        name_with_worksheet = sheet_name
    else:
        name_with_worksheet = worksheet

    if "singular_table_name" in config and config["singular_table_name"]:
        stream_name = underscore(parameterize(name_with_worksheet))
    else:
        stream_name = tableize(parameterize(name_with_worksheet))

    schema = gsheets_loader.get_schema(sheet_name, worksheet)
    records = gsheets_loader.get_data(sheet_name, worksheet)

    # additional data transformations
    column_mapping = None
    if "underscore_columns" in config and config["underscore_columns"]:
        column_mapping = {"id": "id"}
        props = {}
        for k, v in schema["properties"].items():
            kt = underscore(parameterize(k))
            props[kt] = v
            column_mapping[k] = kt
        schema["properties"] = props

    schema["properties"]["id"] = {"type": "integer"}

    for i, record in enumerate(records, start=1):
        record["id"] = i

    # write stuff
    singer.write_schema(stream_name=stream_name, schema=schema, key_properties=["id"])


    for record in records:
        if column_mapping is not None:
            record_transformed = {column_mapping[k]: v for k, v in record.items()}
        else:
            record_transformed = record

        singer.write_record(stream_name, record_transformed)


def main():
    # parse arguments. get config file path.
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="config file", required=True)
    parser.add_argument(
        "-o",
        "--overrides",
        type=json.loads,
        help="a JSON string with configuration overrides",
        required=False,
        default="{}",
    )
    args = parser.parse_args()

    # the configuration file can be provided in json as much as in hocon
    # ConfigFactory will pick up the format from the file extension
    config = ConfigFactory.parse_file(args.config)

    # we like to keep the config as a dict from here on
    config = config.as_plain_ordered_dict()

    # now we override file config with command line provided config
    config.update(args.overrides)

    # go on processing
    sync(config)


if __name__ == "__main__":
    main()
