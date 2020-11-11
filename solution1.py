import logging
import json
from dataclasses import dataclass
from typing import Dict, IO, List
import re
import csv
import argparse


"""
Tasks for program

* Note this solution is dependent on all dictionaries being ordered,
* which has been the case since Python 3.6 (kinda)
* and officially since 3.7
"""

log = logging.getLogger("fixed_width_parser")


@dataclass(frozen=True)
class FixedParserConfig:
    column_names: List[str]
    offsets: List[int]
    fixed_width_encoding: str
    delimited_encoding: str
    include_header: bool


def config_factory(**kwargs) -> FixedParserConfig:
    camel = {}
    for key, value in kwargs.items():
        name = re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()
        camel[name] = value

    return FixedParserConfig(**camel)


class FixedWidthParser:
    def __init__(self, config: FixedParserConfig):
        self.columns = dict(zip(config.column_names, config.offsets))
        self.line_length = sum(int(i) for i in self.columns.values())
        self.output_encoding = config.delimited_encoding
        self.input_encoding = config.fixed_width_encoding
        self.include_header = config.include_header

    def parse_file(self, in_filename: str, out_filename: str):
        with open(in_filename, "rb") as input_file:
            with open(out_filename, "w", encoding=self.output_encoding) as output_file:
                self.parse_stream(input_file, output_file)

    def parse_stream(self, input_file: IO, output_file: IO):
        csv_out = csv.DictWriter(output_file, fieldnames=self.columns.keys())
        if self.include_header:
            csv_out.writeheader()

        while True:
            line: bytes = input_file.read(self.line_length)
            if len(line) == self.line_length:
                csv_out.writerow(self.parse_line(line))
            elif len(line) == 0:
                break
            else:
                log.warning("found incomplete line")
                break

    def parse_line(self, data: bytes) -> Dict[str, str]:
        pos = 0
        output = {}
        for name, length in self.columns.items():
            y = pos + length
            output[name] = data[pos:y].decode(self.input_encoding)
            pos = y

        return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="the fixed length input file")
    parser.add_argument("output_file", help="the output file")
    parser.add_argument(
        "--spec", default="spec.json", help="the specification file (JSON format)"
    )
    args = parser.parse_args()

    with open(args.spec) as spec:
        config = json.load(spec)

    f = FixedWidthParser(config_factory(**config))
    f.parse_file(args.input_file, args.output_file)
