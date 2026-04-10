############################################
##
## Class: ComplianceDisclosures
##
## Purpose: Provide in‑context AI disclosure and a data‑use summary for an internal RAG/LLM assistant.
## Classification: EU AI Act — limited risk (internal dev/QA tool); therefore transparency message is created.
##
############################################

class ComplianceDisclosures:
    def __init__(self, llm_active: bool, retention_days:int) -> None:
        self.llm_active = llm_active
        self.retention_days = retention_days

    def ai_notice(self) -> str:

        if self.llm_active:
            return (
                "========== EU AI Act – Limited Risk System ==========\n\n"
                "You are interacting with an AI system combining semantic search and a language model. "
                "Outputs may be inaccurate and should be reviewed before use."
            )
        else:
            return (
                "========== EU AI Act – Limited Risk System ==========\n\n"
                "You are interacting with an AI system using semantic search. "
                "Results may be incomplete or inaccurate and should be reviewed before use."
        )

        
    def data_use_summary(self) -> str:

        preamble = (
            "This system suggests similar requirements. "
            "Sources are shown for review. Final responsibility remains with the user.\n"
        )

        if self.llm_active:
            return (
                preamble +
                f"Data use: Queries and selected content are processed by an external LLM provider "
                f"(retained for {self.retention_days} days)."
            )
        else:
            return (
                preamble +
                "Data use: Queries are processed locally via semantic search."
            )

    
    def compliance_dict(self) -> dict:
        return {
            "ai_notice": self.ai_notice(),
            "data_use_summary": self.data_use_summary(),
            "version": "2026-03"
        }