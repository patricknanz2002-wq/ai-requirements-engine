import os
import re
import json
import numpy as np
from openai import OpenAI
from embedding.embedder import RequirementsEmbedder


class LLMEvaluator:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key or api_key.strip() == "":
            raise RuntimeError(
                "\n\nNo OPENAI_API_KEY configured.\n"
                "To use the LLM, set the environment variable:\n\n"
                "export OPENAI_API_KEY=<your_api_key>\n"
            )

        try:
            self.client = OpenAI(api_key=api_key)

        except Exception as e:
            raise RuntimeError(f"\n[LLM initialization error]\n{str(e)}")
        

    def cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


    def explanation_similarity_check(self, llm_answers: list, results: list, threshold=0.75):

        encoder = RequirementsEmbedder()

        total = 0
        suspicious = 0

        for entry, answer in zip(results, llm_answers):

            # Map ID → Requirement Text
            req_map = {
                rid: text for rid, text in zip(entry["results"], entry["texts"])
            }

            # Regex: extract REQ + Reason
            pattern = r"\[(REQ-\d+)\].*?Reason:\s*(.*?)(?=\n\d+\.|\Z)"
            matches = re.findall(pattern, answer, re.DOTALL)

            for req_id, reason in matches:

                reason = reason.strip()

                if req_id not in req_map:
                    continue  # safety

                total += 1

                requirement_text = req_map[req_id]

                # Embeddings
                vectors = encoder.encode([reason, requirement_text])
                reason_vec, req_vec = vectors[0], vectors[1]

                sim = self.cosine_similarity(reason_vec, req_vec)

                if sim < threshold:
                    suspicious += 1

        return suspicious / total if total else 0.0


    def invalid_id_rate(self, llm_answers: list, results: list):

        total = 0
        violations = 0
        violation_cases = []

        for entry, answer in zip(results, llm_answers):

            allowed_ids = set(rid.lower() for rid in entry["results"])
            found_ids = set(re.findall(r"req-\d+", answer.lower()))

            total += 1

            invalid_ids = found_ids - allowed_ids

            if invalid_ids:
                violations += 1
                violation_cases.append({
                    "query": entry["query"],
                    "invalid_ids": list(invalid_ids)
                })

        return {
            "rate": violations / total if total else 0.0,
            "count": violations,
            "cases": violation_cases
        }


    def judgement(self, results:list, answers:list) -> list:

        return_list = []

        if len(results) != len(answers):
            raise ValueError("Mismatch between results and answers")

        for entry, llm_answer in zip(results,answers):

            query = entry['query']
            lines = []
            for rid, text, score in zip(entry["results"], entry["texts"], entry["scores"]):
                lines.append(f"{rid} | {text} | {score:.3f}")

            context_str = "\n".join(lines)

            prompt = f"""
                You are a strict evaluator.

                User query:
                {query}

                Context:
                {context_str}

                Answer:
                {llm_answer}

                Evaluate step by step:

                1. Is the answer fully supported by the context?
                2. Does the reasoning match the context?
                3. Does it introduce any new information not in the context?

                Rules:
                - Explanatory phrasing do NOT count as hallucination.
                - Only check whether requirement IDs and their meaning match the context.
                - If hallucination → incorrect
                - Using any ID not listed in the candidate requirements is considered incorrect.

                Output ONLY valid JSON:

                {{"verdict": "correct"}}

                OR

                {{"verdict": "incorrect", "reason": "<short reason>"}}
            """
            response_content = ""
            try:
                response = self.client.chat.completions.create(
                    model="gpt-5.1", messages=[{"role": "user", "content": prompt}]
                )
                response_content = response.choices[0].message.content

            except Exception as e:
                return f"LLM error: {str(e)}"

            return_list.append({
                "query" : query,
                "judgment" : response_content
            })
        
        return return_list
    
    
    def parse_judgment(self, raw_judgment: str) -> tuple[str, str]:

        try:
            data = json.loads(raw_judgment)
            verdict = data.get("verdict")
            reason = data.get("reason", "")
            return verdict, reason

        except Exception:
            # fallback
            raw = raw_judgment.strip()
            is_incorrect = re.match(r"^\s*incorrect\b", raw.lower())

            if is_incorrect:
                return "incorrect", raw

            return "unknown", raw


    def output_answer(self, query, similar_requirements) -> str:

            lines = []

            for req_id, text, score in similar_requirements:
                line = f"{req_id} | {text} | {score:.3f}"
                lines.append(line)

            formatted_requirements = "\n".join(lines)

            prompt = f"""
            User requirement:
            {query}

            Candidate requirements:
            {formatted_requirements}

            Each requirement has the format:
            id | requirement_text | similarity_score

            Task:
            Explain why the most similar requirements match the user requirement.

            Rules:
            - The requirements are already ranked by similarity_score
            - Do NOT invent new requirements
            - Use the similarity score exactly as given
            - Keep explanations short (1 sentence)
            - You MUST ONLY use the provided requirement IDs. Do NOT generate new IDs. If unsure, use only the given ones.

            Output format:

            LLM Response:

            1. [<id>] <requirement text>
            Similarity: <score as percentage>
            Reason: <short explanation>

            2. [<id>] <requirement text>
            Similarity: <score as percentage>
            Reason: <short explanation>

            """

            try:
                response = self.client.chat.completions.create(
                    model="gpt-5.1", messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content

            except Exception as e:
                return f"LLM error: {str(e)}"
            

    def tokenize(self, text):
        return re.findall(r"\b\w+\b", text.lower())


    def collect_llm_outputs(self, results:list) -> list:

        returnList = []

        for entry in results:

            query = entry['query']
            result_ids = entry['results']
            scores = entry['scores']
            retrieved_texts = entry['texts']
            similar_results = [
                (rid, text, score)
                for rid, text, score in zip(result_ids, retrieved_texts, scores)]

            returnList.append(self.output_answer(query,similar_results))

        return returnList
    

    def common_words_ratio(self, llm_answers:list, results:list)-> float:

        conncated_answers = " ".join(llm_answers)
        conncated_texts = ""

        all_texts = []
        for entry in results:
            all_texts.extend(entry['texts'])
        conncated_texts = " ".join(all_texts)

        answer_set = set(self.tokenize(conncated_answers))
        text_set = set(self.tokenize(conncated_texts))
        overlap = answer_set.intersection(text_set)
        
        return len(overlap) / len(answer_set) if answer_set else 0.0
    

    def retrieved_id_coverage(self, llm_answers:list, results:list) -> float:

        conncated_answers = " ".join(llm_answers)

        all_ids = []
        for entry in results:
            all_ids.extend(entry['results'])

        id_set = {rid.lower() for rid in all_ids}
        found_ids = set(re.findall(r"req-\d+", conncated_answers.lower()))
        matches = id_set.intersection(found_ids)

        return len(matches) / len(id_set) if id_set else 0.0


    def summarize_llm(self, results: list) -> dict:

        llm_answers = self.collect_llm_outputs(results)
        id_check = self.invalid_id_rate(llm_answers, results)

        summary = {}
        grounding = {}

        # Groundness
        summary["common_words_ratio"] = self.common_words_ratio(llm_answers, results)
        summary["retrieved_id_coverage"] = self.retrieved_id_coverage(llm_answers, results)

        # LLM Judge
        judgment_list = self.judgement(results, llm_answers)

        correct = 0
        incorrect = 0
        unknown = 0
        incorrect_cases = []

        for entry in judgment_list:
            verdict, reason = self.parse_judgment(entry["judgment"])

            if verdict == "correct":
                correct += 1
            elif verdict == "incorrect":
                incorrect += 1
                incorrect_cases.append({
                    "query": entry["query"],
                    "reason": reason
                })
            else:
                unknown += 1

        total = len(judgment_list)

        summary["accuracy"] = correct / total if total else 0.0
        summary["correct"] = correct
        summary["incorrect"] = incorrect
        summary["unknown"] = unknown

        # Semantic grounding
        grounding["mismatch_rate"] = self.explanation_similarity_check(llm_answers, results)

        return {
            "summary": summary,
            "grounding": grounding,
            "incorrect_cases": incorrect_cases,
            "id_check": id_check
        }
    
    def print_llm_output(self, evaluation: dict):

        summary = evaluation["summary"]
        grounding = evaluation["grounding"]
        incorrect_cases = evaluation["incorrect_cases"]
        id_check = evaluation["id_check"]

        label_width = 22

        def row(label, value):
            print(f"{label:<{label_width}} : {value}")

        print("\n=======================================")
        print("============ LLM Evaluation ===========")
        print("=======================================")

        print("\n============= Groundness =============")
        row("Overlap Ratio", f"{summary['common_words_ratio']:.2f}")
        row("ID Coverage", f"{summary['retrieved_id_coverage']:.2f}")

        print("\n============= LLM Score =============")
        row("Accuracy", f"{summary['accuracy']:.2f}")
        row("Correct", summary['correct'])
        row("Incorrect", summary['incorrect'])
        row("Unknown", summary['unknown'])

        print("\n============= Semantic Grounding =============")
        row("Mismatch Rate", f"{grounding['mismatch_rate']:.2f}")

        print("\n============= ID Consistency =============")
        row("Invalid ID Rate", f"{id_check['rate']:.2f}")
        row("Violations", id_check['count'])

        print("\n============= Incorrect Cases =============")

        if not incorrect_cases:
            print("All answers are correct.")
        else:
            for case in incorrect_cases:
                print(f"\nQuery   : {case['query']}")
                print(f"Reason  : {case['reason']}")

        print("\n========================================")
        print("=========== End of Evaluation ==========")
        print("========================================\n")