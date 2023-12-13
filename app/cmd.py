from dataclasses import dataclass, field
from pathlib import Path

data_directory = Path(__file__).parent.parent / "data"


@dataclass
class PandocCmd:
    source: str = f"{data_directory}/resume.md"
    output: str = f"{data_directory}/resume.pdf"
    filter: str = "pandoc-crossref"
    process_cite: bool = False
    pdf_engine: str = "lualatex"
    variables: dict[str, str] = field(
        default_factory=lambda: {"luatexjapresetoptions": "ipa"}
    )
    number_sections: bool = True

    def command(self) -> list[str]:
        cmd = ["pandoc"]
        cmd.extend(["--filter", self.filter])

        if self.process_cite:
            cmd.append("--citeproc")

        cmd.extend(["--pdf-engine", self.pdf_engine])

        for key, val in self.variables.items():
            cmd.extend(["--variable", f"{key}:{val}"])

        if self.number_sections:
            cmd.append("--number-sections")

        cmd.extend(["--output", self.output])
        cmd.append(self.source)

        return cmd
