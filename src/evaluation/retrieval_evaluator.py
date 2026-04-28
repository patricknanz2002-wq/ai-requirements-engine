from test_set_definition import TEST_SETS, TOP_K, THRESHOLD


############################################
##
## Class: RetrievalEvaluator
##
############################################
class RetrievalEvaluator:
    def __init__(self):
        pass


    ############################################
    ##
    ## Method: hit_rate_at_k
    ## Description: Measures how often at least one
    ## expected document appears in the top-k results
    ##
    ############################################
    def hit_rate_at_k(self, results: list) -> float:
        count = 0

        for entry in results:
            has_match = not set(entry["expected"]).isdisjoint(entry["results"])
            if has_match:
                count += 1

        return count / len(results)


    ############################################
    ##
    ## Method: failed_cases
    ## Description: Returns all queries where
    ## no expected result was retrieved
    ##
    ############################################
    def failed_cases(self, results: list) -> list:
        failed_queries = []

        for entry in results:
            has_match = not set(entry["expected"]).isdisjoint(entry["results"])
            if not has_match:
                failed_queries.append(entry)

        return failed_queries


    ############################################
    ##
    ## Method: recall
    ## Description: Recall per query
    ## (fraction of relevant documents retrieved)
    ##
    ############################################
    def recall(self, results: list) -> list:
        recall_list = []

        for entry in results:
            result_set = set(entry["results"])
            matches = [val for val in entry["expected"] if val in result_set]

            recall = len(matches) / len(entry["expected"])

            recall_list.append({
                "query": entry["query"],
                "recall": recall
            })

        return recall_list


    ############################################
    ##
    ## Method: precision
    ## Description: Precision per query
    ## (fraction of retrieved documents that are relevant)
    ##
    ############################################
    def precision(self, results: list) -> list:
        precision_list = []

        for entry in results:
            expected_set = set(entry["expected"])
            matches = [val for val in entry["results"] if val in expected_set]

            precision = len(matches) / len(entry["results"])

            precision_list.append({
                "query": entry["query"],
                "precision": precision
            })

        return precision_list


    ############################################
    ##
    ## Method: is_low_score
    ## Description: Checks whether a score is below
    ## the global threshold
    ##
    ############################################
    def is_low_score(self, value: float) -> bool:
        return value < THRESHOLD
    

    ############################################
    ##
    ## Method: delta_top2
    ## Description: Difference between top-1 and top-2 score
    ## → indicates ranking stability
    ##
    ############################################
    def delta_top2(self, scores:list) -> float:
        if len(scores) < 2:
            return 0.0
        else:
            return scores[0] - scores[1]
        

    ############################################
    ##
    ## Method: retrieval_confidence
    ## Description: Combines absolute score and margin
    ## → estimates confidence in top result
    ##
    ############################################
    def retrieval_confidence(self, scores: list) -> float:
        if len(scores) < 2:
            return 0.0
        return scores[0] * (scores[0] - scores[1])
    

    ############################################
    ##
    ## Method: score_distribution
    ## Description: Returns statistical overview of scores
    ##
    ############################################
    def score_distribution(self, scores: list) -> dict:
        if not scores:
            return {}

        return {
            "max": scores[0],
            "min": scores[-1],
            "avg": sum(scores) / len(scores),
            "spread": scores[0] - scores[-1]
        }


    ############################################
    ##
    ## Method: is_confident
    ## Description: Determines whether retrieval is reliable
    ## based on threshold + score margin
    ##
    ############################################
    def is_confident(self, scores: list, threshold=THRESHOLD, delta=0.1) -> bool:
        if len(scores) < 2:
            return False
        return scores[0] >= threshold and (scores[0] - scores[1]) >= delta


    ############################################
    ##
    ## Method: top1_hit
    ## Description: Checks if the top-1 result is correct
    ##
    ############################################
    def top1_hit(self, entry: dict) -> bool:
        return entry["results"][0] in entry["expected"]


    ############################################
    ##
    ## Method: topk_hit
    ## Description: Checks if any top-k result is correct
    ##
    ############################################
    def topk_hit(self, entry: dict) -> bool:
        return not set(entry["expected"]).isdisjoint(entry["results"])


    ############################################
    ##
    ## Method: false_positives
    ## Description: Returns retrieved IDs that are incorrect
    ##
    ############################################
    def false_positives(self, entry: dict) -> list:
        expected = set(entry["expected"])
        return [rid for rid in entry["results"] if rid not in expected]


    ############################################
    ##
    ## Method: score_evaluation
    ## Description: Evaluates retrieval quality per query
    ## using score-based heuristics
    ##
    ############################################
    def score_evaluation(self, results:list) -> list:
        return_list = []

        for entry in results:
            scores = entry["scores"]
            top_score = scores[0]
            delta_score = self.delta_top2(scores)
            confidence = self.retrieval_confidence(scores)
            distribution = self.score_distribution(scores)
            is_confident = self.is_confident(scores)
            top1 = self.top1_hit(entry)
            topk = self.topk_hit(entry)

            status = ""

            if delta_score < 0.1:
                status = "unsafe"
            else:
                status = "safe"

            return_list.append({
                 "query": entry["query"],
                 "top_score": top_score,
                 "top2_delta": delta_score,
                 "evaluation": status,
                 "confidence": confidence,
                 "is_confident" : is_confident,
                 "distribution" : distribution,
                 "top1" : top1,
                 "topk" : topk
            })    

        return return_list


    ############################################
    ##
    ## Method: summarize_retrieval
    ## Description: Aggregates all metrics into a summary
    ##
    ############################################
    def summarize_retrieval(self, results: list) -> dict:

        return_dict = {}
        summary = {}
        distribution_summary = {}
        cases_of_interest = []

        summary["number_of_test_cases"] = len(TEST_SETS)

        # Hit Rate @ k
        summary[f"hit_rate@{TOP_K}"] = self.hit_rate_at_k(results)

        # Recall
        recall_list = self.recall(results)
        recall_avg = sum(r["recall"] for r in recall_list) / len(recall_list)
        summary["recall_avg"] = recall_avg

        # Precision
        precision_list = self.precision(results)
        precision_avg = sum(p["precision"] for p in precision_list) / len(precision_list)
        summary["precision_avg"] = precision_avg

        # Detailed metrics aggregation
        topk_count = 0
        top1_count = 0
        unsafe_count = 0
        confidence = 0
        top_score = 0
        top2_delta = 0
        score_spread = 0
        low_confidence_count = 0

        score_evaluation_list = self.score_evaluation(results)

        for entry in score_evaluation_list:
            if entry['top1']:
                top1_count += 1
            if entry['topk']:
                topk_count += 1
            if entry['evaluation'] == "unsafe":
                unsafe_count += 1
            if not entry['is_confident']:
                low_confidence_count += 1

            confidence += entry['confidence']
            top_score += entry['top_score']
            top2_delta += entry['top2_delta']

            distribution = entry['distribution']
            score_spread += distribution['spread']

            if entry['evaluation'] == "unsafe" or entry['top_score'] < THRESHOLD or entry in self.failed_cases(results):

                case_of_interest = {
                    "query": entry['query'],
                    "top_score": entry['top_score'],
                    "delta": entry['top2_delta'],
                    "top1": entry['top1'],
                    "topk": entry['topk'],
                    "reason": entry['evaluation']
                }
                cases_of_interest.append(case_of_interest)  
            
        summary["top1_accuracy"] = top1_count / len(results)
        summary["topk_accuracy"] = topk_count / len(results)
        summary["unsafe_ratio"] = unsafe_count / len(results)
        summary["low_confidence_ratio"] = low_confidence_count / len(results)
        summary["confidence_avg"] = confidence / len(results)

        distribution_summary["top_score_avg"] = top_score / len(results)
        distribution_summary["top2_delta_avg"] = top2_delta / len(results)
        distribution_summary["score_spread_avg"] = score_spread / len(results)

        return_dict["summary"] = summary
        return_dict["distribution"] = distribution_summary
        return_dict["cases_of_interest"] = cases_of_interest

        return return_dict


    ############################################
    ##
    ## Method: print_output
    ## Description: Pretty-prints evaluation results
    ##
    ############################################
    def print_output(self, evaluation: dict):

        summary = evaluation["summary"]
        distribution = evaluation["distribution"]
        cases = evaluation["cases_of_interest"]

        label_width = 20

        def row(label, value):
            print(f"{label:<{label_width}} : {value}")

        print("\n=================================")
        print("====== Retrieval Evaluation =====")
        print("=================================\n")

        print("========== SUMMARY ==========")
        row("Test Cases", summary['number_of_test_cases'])
        row(f"Hit Rate @{TOP_K}", f"{summary[f'hit_rate@{TOP_K}']:.2f}")
        row("Recall Avg", f"{summary['recall_avg']:.2f}")
        row("Precision Avg", f"{summary['precision_avg']:.2f}")
        row("Top1 Accuracy", f"{summary['top1_accuracy']:.2f}")
        row("TopK Accuracy", f"{summary['topk_accuracy']:.2f}")
        row("Unsafe Ratio", f"{summary['unsafe_ratio']:.2f}")
        row("Low Confidence", f"{summary['low_confidence_ratio']:.2f}")
        row("Avg Confidence", f"{summary['confidence_avg']:.2f}")

        print("\n========== SCORE DISTRIBUTION ==========")
        row("Avg Top Score", f"{distribution['top_score_avg']:.2f}")
        row("Avg Delta Top2", f"{distribution['top2_delta_avg']:.2f}")
        row("Avg Score Spread", f"{distribution['score_spread_avg']:.2f}")

        print("\n========== CASES OF INTEREST ==========")

        if not cases:
            print("No problematic cases found")
        else:
            for case in cases:
                print(f"\nQuery      : {case['query']}")
                print(f"Top Score  : {case['top_score']:.2f}")
                print(f"Delta      : {case['delta']:.2f}")
                print(f"Top1/TopK  : {case['top1']} / {case['topk']}")
                print(f"Reason     : {case['reason']}")

        print("\n========================================")
        print("===== End of Retrieval Evaluation ======")
        print("========================================\n")