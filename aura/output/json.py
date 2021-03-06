from dataclasses import dataclass
from typing import Any

from .base import ScanOutputBase, DiffOutputBase, TyposquattingOutputBase
from ..type_definitions import DiffType, DiffAnalyzerType
from ..json_proxy import dumps


class JSONOutputBase:
    @classmethod
    def protocol(cls) -> str:
        return "json"


@dataclass()
class JSONScanOutput(JSONOutputBase, ScanOutputBase):
    _fd: Any = None

    def __enter__(self):
        if self.output_location == "-":
            return

        self._fd = open(self.output_location, "w")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._fd:
            self._fd.close()

    def output(self, hits, scan_metadata: dict):
        score = 0
        tags = set()

        for x in hits:
            tags |= x.tags
            score += x.score

        data = {
            "detections": [x._asdict() for x in hits],
            "imported_modules": list(
                {x.extra["name"] for x in hits if x.name == "ModuleImport"}
            ),
            "tags": list(tags),
            "metadata": scan_metadata,
            "score": score,
            "name": scan_metadata["name"],
        }

        print(dumps(data), file=self._fd)


@dataclass()
class JSONDiffOutput(JSONOutputBase, DiffOutputBase):
    _fd: Any = None

    def __enter__(self):
        if self.output_location == "-":
            return

        self._fd = open(self.output_location, "w")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._fd:
            self._fd.close()

    def output_diff(self, diff_analyzer: DiffAnalyzerType):
        payload = {
            "tables": [],
            "diffs": []
        }

        for table in diff_analyzer.tables:
            payload["tables"].append(table.asdict())

        for d in self.filtered(diff_analyzer.diffs):  # type: DiffType
            diff = {
                "operation": d.operation,
                "a_ref": d.a_ref,
                "b_ref": d.b_ref,
                "a_size": d.a_size,
                "b_size": d.b_size,
                "a_mime": d.a_mime,
                "b_mime": d.b_mime,
                "a_md5": d.a_md5,
                "b_md5": d.b_md5,
                "similarity": d.similarity
            }

            if d.new_detections:
                diff["new_detections"] = [x._asdict() for x in d.new_detections]

            if d.removed_detections:
                diff["removed_detections"] = [x._asdict() for x in d.removed_detections]

            if d.diff and self.patch:
                diff["diff"] = d.diff

            payload["diffs"].append(diff)

        print(dumps(payload), file=self._fd)


class JSONTyposquattingOutput(TyposquattingOutputBase):
    @classmethod
    def protocol(cls) -> str:
        return "json"

    def output_typosquatting(self, entries):
        for x in entries:
            data = {
                "original": x["original"],
                "typosquatting": x["typo"],
                "original_score": x["orig_score"].get_score_matrix(),
                "typosquatting_score": x["typo_score"].get_score_matrix(),
            }
            print(dumps(data))
