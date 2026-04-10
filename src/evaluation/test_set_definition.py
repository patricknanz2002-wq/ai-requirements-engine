############################################
##
## Test Set Definition
##
############################################

TOP_K = 3
THRESHOLD = 0.5

TEST_SETS = [
    {
        "query": "system protection and security mechanisms",
        "expected_ids": ["REQ-0134", "REQ-0042"]
    },
    {
        "query": "testing and verification of components",
        "expected_ids": ["REQ-0007", "REQ-0049"]
    },
    {
        "query": "audio playback behavior in system",
        "expected_ids": ["REQ-0091", "REQ-0094"]
    },
    {
        "query": "handling system failures and errors",
        "expected_ids": ["REQ-0017", "REQ-0023"]
    }
]