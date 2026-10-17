import json
import sys
import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from toolbox import LEDGER, get_summary, plot_distribution, record_classification
from toolbox.get_summary import GetSummaryInput
from toolbox.record_classification import RecordClassificationInput


class HcahpsToolboxTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        LEDGER.clear()

    def test_record_schema_is_strict_and_descriptive(self) -> None:
        schema = record_classification.to_json_schema_spec()
        parameters = schema["function"]["parameters"]

        self.assertFalse(parameters["additionalProperties"])
        self.assertEqual(
            parameters["required"],
            ["comment_id", "label", "confidence", "rationale"],
        )
        self.assertEqual(
            parameters["properties"]["confidence"]["enum"],
            ["low", "medium", "high"],
        )
        self.assertIn("description", parameters["properties"]["rationale"])

    def test_models_reject_invalid_and_extra_arguments(self) -> None:
        with self.assertRaises(ValidationError):
            GetSummaryInput.model_validate(
                {"group_by": "invalid", "unexpected": True}
            )

        with self.assertRaises(ValidationError):
            RecordClassificationInput.model_validate(
                {
                    "comment_id": 0,
                    "label": "other",
                    "confidence": "high",
                    "rationale": " ",
                }
            )

    async def test_tools_share_one_ledger(self) -> None:
        record_contents = await record_classification.invoke(
            arguments={
                "comment_id": 1,
                "label": "communication_nurses",
                "confidence": "high",
                "rationale": "The patient described communication with a nurse.",
            }
        )
        record_result = json.loads(record_contents[0].text)

        summary_contents = await get_summary.invoke(
            arguments={"group_by": "label"}
        )
        summary_result = json.loads(summary_contents[0].text)

        self.assertEqual(record_result["recorded_total"], 1)
        self.assertEqual(summary_result["total_comments"], 1)
        self.assertEqual(
            summary_result["counts"],
            {"communication_nurses": 1},
        )

    async def test_plot_reports_empty_ledger_without_creating_artifact(self) -> None:
        contents = await plot_distribution.invoke(
            arguments={"group_by": "confidence"}
        )
        result = json.loads(contents[0].text)

        self.assertFalse(result["created"])
        self.assertEqual(result["summary"]["total_comments"], 0)
        self.assertEqual(list(Path(self.temporary_directory.name).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
