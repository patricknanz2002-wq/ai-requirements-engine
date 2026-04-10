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

        header = (
            "----------------------------------------\n"
            "AI Transparency Notice (EU AI Act)\n"
            "----------------------------------------"
        )

        if self.llm_active:
            body = (
                "[i] AI-assisted retrieval (semantic search + LLM)\n"
                "[i] Results may be inaccurate\n"
                "[i] Human review required"
            )
        else:
            body = (
                "[i] AI-assisted retrieval (semantic search)\n"
                "[i] Results may be incomplete or inaccurate\n"
                "[i] Human review required"
            )

        return f"{header}\n\n{body}"
        
    def data_use_summary(self) -> str:

        if self.llm_active:
            return (
                "Data use:\n"
                "- Queries and selected content sent to external LLM\n"
                f"- Retention: {self.retention_days} days"
            )
        else:
            return (
                "\nData use:\n"
                "- Queries are processed locally\n"
                "- Based on internal requirements"
            )    
        
    def compliance_dict(self) -> dict:
        return {
            "ai_notice": self.ai_notice(),
            "data_use_summary": self.data_use_summary(),
            "version": "ai-act-disclosure-v1"
        }