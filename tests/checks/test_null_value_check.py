from unittest import TestCase

import pandas as pd

from focus_validator.config_objects import Rule
from focus_validator.config_objects.common import (
    AllowNullsCheck,
    DataTypeConfig,
    DataTypes,
    ChecklistObjectStatus,
)
from focus_validator.config_objects.rule import ValidationConfig
from focus_validator.rules.spec_rules import SpecRules


# noinspection DuplicatedCode
class TestNullValueCheck(TestCase):
    @staticmethod
    def __generate_sample_rule_type_string__(allow_nulls: bool, data_type: DataTypes):
        return [
            Rule(
                check_id="allow_null",
                dimension="test_dimension",
                validation_config=ValidationConfig(
                    check=AllowNullsCheck(allow_nulls=allow_nulls),
                    check_friendly_name="",
                ),
            ),
            Rule(
                check_id="test_dimension",
                dimension="test_dimension",
                validation_config=DataTypeConfig(data_type=data_type),
            ),
        ]

    def test_null_value_allowed_valid_case(self):
        rules = self.__generate_sample_rule_type_string__(
            allow_nulls=True, data_type=DataTypes.STRING
        )
        sample_data = pd.DataFrame(
            [{"test_dimension": "NULL"}, {"test_dimension": "some-value"}]
        )

        schema, checklist = Rule.generate_schema(rules=rules, override_config=None)
        validation_result = SpecRules.__validate_schema__(
            pandera_schema=schema, checklist=checklist, focus_data=sample_data
        )
        self.assertIsNone(validation_result.failure_cases)

    def test_null_value_not_allowed_valid_case(self):
        rules = self.__generate_sample_rule_type_string__(
            allow_nulls=False, data_type=DataTypes.STRING
        )
        sample_data = pd.DataFrame(
            [{"test_dimension": "val1"}, {"test_dimension": "val2"}]
        )
        schema, checklist = Rule.generate_schema(rules=rules, override_config=None)
        validation_result = SpecRules.__validate_schema__(
            pandera_schema=schema, checklist=checklist, focus_data=sample_data
        )
        self.assertIsNone(validation_result.failure_cases)

    def test_null_value_not_allowed_invalid_case(self):
        rules = self.__generate_sample_rule_type_string__(
            allow_nulls=False, data_type=DataTypes.STRING
        )
        sample_data = pd.DataFrame(
            [{"test_dimension": "NULL"}, {"test_dimension": "val2"}]
        )
        schema, checklist = Rule.generate_schema(rules=rules, override_config=None)
        validation_result = SpecRules.__validate_schema__(
            pandera_schema=schema, checklist=checklist, focus_data=sample_data
        )
        self.assertEqual(
            validation_result.checklist["allow_null"].status,
            ChecklistObjectStatus.FAILED,
        )
        self.assertIsNotNone(validation_result.failure_cases)
        failure_cases_dict = validation_result.failure_cases.to_dict(orient="records")
        self.assertEqual(len(failure_cases_dict), 1)
        self.assertEqual(
            failure_cases_dict[0],
            {
                "Dimension": "test_dimension",
                "Check Name": "allow_null",
                "Description": " ",
                "Values": "NULL",
                "Row #": 1,
            },
        )

    def test_null_value_allowed_invalid_case_with_empty_strings(self):
        rules = self.__generate_sample_rule_type_string__(
            allow_nulls=True, data_type=DataTypes.STRING
        )
        sample_data = pd.DataFrame([{"test_dimension": "NULL"}, {"test_dimension": ""}])

        schema, checklist = Rule.generate_schema(rules=rules, override_config=None)
        validation_result = SpecRules.__validate_schema__(
            pandera_schema=schema, checklist=checklist, focus_data=sample_data
        )
        self.assertEqual(
            validation_result.checklist["allow_null"].status,
            ChecklistObjectStatus.FAILED,
        )
        self.assertIsNotNone(validation_result.failure_cases)
        failure_cases_dict = validation_result.failure_cases.to_dict(orient="records")
        self.assertEqual(len(failure_cases_dict), 1)
        self.assertEqual(
            failure_cases_dict[0],
            {
                "Dimension": "test_dimension",
                "Check Name": "allow_null",
                "Description": " ",
                "Values": "",
                "Row #": 2,
            },
        )

    def test_null_value_allowed_invalid_case_with_nan_values(self):
        rules = self.__generate_sample_rule_type_string__(
            allow_nulls=True, data_type=DataTypes.STRING
        )
        sample_data = pd.DataFrame(
            [{"test_dimension": "NULL"}, {"test_dimension": None}]
        )

        schema, checklist = Rule.generate_schema(rules=rules, override_config=None)
        validation_result = SpecRules.__validate_schema__(
            pandera_schema=schema, checklist=checklist, focus_data=sample_data
        )
        self.assertEqual(
            validation_result.checklist["allow_null"].status,
            ChecklistObjectStatus.FAILED,
        )
        self.assertIsNotNone(validation_result.failure_cases)
        failure_cases_dict = validation_result.failure_cases.to_dict(orient="records")
        self.assertEqual(len(failure_cases_dict), 1)
        self.assertEqual(
            failure_cases_dict[0],
            {
                "Dimension": "test_dimension",
                "Check Name": "allow_null",
                "Description": " ",
                "Values": None,
                "Row #": 2,
            },
        )

    def test_null_value_allowed_with_decimal_type_valid_case(self):
        pass

    def test_null_value_allowed_with_decimal_type_invalid_case(self):
        pass

    def test_null_value_not_allowed_with_decimal_type_valid_case(self):
        pass

    def test_null_value_not_allowed_with_decimal_type_invalid_case(self):
        rules = self.__generate_sample_rule_type_string__(
            allow_nulls=True, data_type=DataTypes.DECIMAL
        )
        sample_data = pd.DataFrame(
            [{"test_dimension": "NULL"}, {"test_dimension": 0.1}]
        )

        schema, checklist = Rule.generate_schema(rules=rules, override_config=None)
        validation_result = SpecRules.__validate_schema__(
            pandera_schema=schema, checklist=checklist, focus_data=sample_data
        )
        self.assertEqual(
            validation_result.checklist["allow_null"].status,
            ChecklistObjectStatus.FAILED,
        )
        self.assertIsNotNone(validation_result.failure_cases)
        failure_cases_dict = validation_result.failure_cases.to_dict(orient="records")
        self.assertEqual(len(failure_cases_dict), 1)
        self.assertEqual(
            failure_cases_dict[0],
            {
                "Dimension": "test_dimension",
                "Check Name": "allow_null",
                "Description": " ",
                "Values": None,
                "Row #": 2,
            },
        )
