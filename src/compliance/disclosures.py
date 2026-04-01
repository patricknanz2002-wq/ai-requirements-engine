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
            return ("Notice: You are interacting with an AI assistant. "
                    "Suggestions are generated using semantic search and a language model. "
                    "Outputs may contain errors and must be reviewed before use.")
        else:
            return ("Notice: You are interacting with an AI assistant.   "
                    "This system uses semantic search to retrieve similar requirements. "
                    "Results may be incomplete or inaccurate and must be reviewed before use.")

        
    def data_use_summary(self) -> str:

        preamble = ("This assistant uses AI to propose similar requirements. "
                "Sources are shown for your review. Do not rely on the output without human verification; "
                "you remain responsible for final decisions. \n\n")
        
        if self.llm_active:
            return (preamble + 
                    f"Data use: Your query and selected snippets are processed by an external LLM provider. "
                    f"Inputs are retained for {self.retention_days} days. Suggestions are based on internal requirements documents.")
        else:
            return (preamble +
                    "Data use: Your query is processed via semantic search against internal requirements documents.")

    
    def compliance_dict(self) -> dict:
        return {
            "ai_notice": self.ai_notice(),
            "data_use_summary": self.data_use_summary(),
            "version": "2026-03"
        }