import re


############################################
##
## Class: Security Layer
##
############################################
class SecurityLayer:

    def __init__(self):
        pass

    ############################################
    ##
    ## Method: processQuery
    ##
    ############################################
    def processQuery(self, text: str) -> dict:
        """
        Entry point for security processing.

        Applies detection, masking and blocking logic
        to the incoming user query before it is passed
        to embedding or LLM components.
        """

        return_dict = self.filter_sensitive_data(text)
        return return_dict


    ############################################
    ##
    ## Method: filter_sensitive_data
    ##
    ############################################
    def filter_sensitive_data(self, text):
        """
        Detects sensitive data patterns in the input text,
        resolves overlaps using priority rules, and returns
        a sanitized version of the query.

        Also determines whether the input should be blocked
        (e.g. API keys).
        """

        # Define detection patterns with priority and behavior
        patterns = [
            {
                "type": "api_key",
                "regex": r"\b(sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z\-_]{20,}|[A-Za-z0-9_\-]{32,})\b",
                "replacement": "[API_KEY]",
                "priority": 3,
                "block": True
            },
            {
                "type": "email",
                "regex": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
                "replacement": "[EMAIL]",
                "priority": 2,
                "block": False
            },
            {
                "type": "phone",
                "regex": r"(?<!\w)(\+?\d[\d\s\-\(\)]{7,}\d)",
                "replacement": "[PHONE]",
                "priority": 1,
                "block": False
            }
        ]

        matches = []

        ############################################
        ## Step 1: Collect matches on original text
        ############################################
        # Important: operate only on original input to avoid
        # shifting indices during replacements
        for pattern in patterns:
            for match in re.finditer(pattern["regex"], text):
                matches.append({
                    "start": match.start(),
                    "end": match.end(),
                    "type": pattern["type"],
                    "original": match.group(0),
                    "replacement": pattern["replacement"],
                    "priority": pattern["priority"],
                    "block": pattern["block"]
                })

        ############################################
        ## Step 2: Sort matches
        ############################################
        # Sorting logic:
        # 1. earlier position first
        # 2. higher priority first
        # 3. longer match first
        matches.sort(key=lambda x: (x["start"], -x["priority"], -(x["end"] - x["start"])))

        ############################################
        ## Step 3: Resolve overlaps
        ############################################
        # Ensures deterministic behavior when multiple
        # patterns match overlapping regions
        filtered_matches = []

        for m in matches:
            overlap = False

            for existing in filtered_matches:
                if not (m["end"] <= existing["start"] or m["start"] >= existing["end"]):
                    overlap = True
                    break

            if not overlap:
                filtered_matches.append(m)

        ############################################
        ## Step 4: Reconstruct sanitized string
        ############################################
        result = []
        last_index = 0
        detections = []
        blocked = False

        for m in filtered_matches:
            # Keep unchanged text before match
            result.append(text[last_index:m["start"]])

            # Insert replacement token
            result.append(m["replacement"])

            last_index = m["end"]

            # Store detection metadata (internal use)
            detections.append({
                "type": m["type"],
                "original": m["original"],
                "replacement": m["replacement"],
                "start": m["start"],
                "end": m["end"]
            })

            # Check if this match requires blocking
            if m["block"]:
                blocked = True

        # Append remaining text
        result.append(text[last_index:])

        ############################################
        ## Final Output
        ############################################
        return {
            "sanitized_query": "".join(result),
            "detections": detections,
            "blocked": blocked
        }