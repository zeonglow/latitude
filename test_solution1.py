import unittest
import io
import os
from solution1 import FixedWidthParser, FixedParserConfig, config_factory

sample_config = {
    "ColumnNames": [
        "f1",
        "f2",
        "f3",
    ],
    "Offsets": [
        5,
        7,
        3,
    ],
    "FixedWidthEncoding": "windows-1252",
    "IncludeHeader": "True",
    "DelimitedEncoding": "utf-8",
}


class TestSolution1(unittest.TestCase):
    """
    I prefer using pytest, but it's a little heavyweight for this example

    """

    def test_config_factory(self):
        result = config_factory(**sample_config)
        self.assertEqual(result.column_names, ["f1", "f2", "f3"])
        self.assertEqual(result.offsets, [5, 7, 3])
        self.assertEqual(result.fixed_width_encoding, "windows-1252")
        self.assertEqual(result.delimited_encoding, "utf-8")

    def test_line_parsing1(self):
        config = FixedParserConfig(
            ["a", "b", "c"],
            [3, 5, 3],
            "utf-8",
            "utf-8",
            False,
        )

        parser = FixedWidthParser(config)

        result = parser.parse_line(b"xxxdddddqqq")

        self.assertEqual(result["a"], "xxx")
        self.assertEqual(result["b"], "ddddd")
        self.assertEqual(result["c"], "qqq")

    def test_line_parsing_with_whitespace(self):
        config = FixedParserConfig(
            ["a", "b", "c"],
            [3, 5, 3],
            "utf-8",
            "utf-8",
            False,
        )
        parser = FixedWidthParser(config)

        result = parser.parse_line(b"aaaeeeeepp ")

        self.assertEqual(result["a"], "aaa")
        self.assertEqual(result["b"], "eeeee")
        self.assertEqual(result["c"], "pp ")

    def test_end_to_end(self):
        config = FixedParserConfig(
            ["a", "b", "c"],
            [3, 5, 3],
            "utf-8",
            "utf-8",
            False,
        )
        parser = FixedWidthParser(config)
        in_buffer = io.BytesIO()
        in_buffer.write(b"123abcde123")
        in_buffer.write(b"456fghij456")
        in_buffer.write(b"789klmno789")
        in_buffer.seek(0)

        out_buffer = io.StringIO()

        parser.parse_stream(in_buffer, out_buffer)

        result = [line for line in out_buffer.getvalue().split("\r\n")]

        self.assertEqual(result[0], "123,abcde,123")
        self.assertEqual(result[1], "456,fghij,456")
        self.assertEqual(result[2], "789,klmno,789")


if __name__ == "__main__":
    unittest.main()
