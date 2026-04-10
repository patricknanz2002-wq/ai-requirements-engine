import os

from dotenv import load_dotenv
from openai import OpenAI


class LLMService:
    def __init__(self):

        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key or api_key.strip() == "":
            raise RuntimeError(
                "No OPENAI_API_KEY configured.\n"
            )

        try:
            self.client = OpenAI(api_key=api_key)

        except Exception as e:
            raise RuntimeError(f"\n[LLM initialization error]\n{str(e)}")

    def output_answer(self, query, similar_requirements):

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

        After listing the requirements, generate a humorous hiring hint.

        IMPORTANT RULES FOR THE HIRING HINT:
        - It must be exactly one sentence
        - It must start with the exact phrase: "You should hire Patrick because"
        - Do not add anything before or after the sentence

        Output format:

        LLM Response:

        1. [<id>] <requirement text>
        Similarity: <score as percentage>
        Reason: <short explanation>

        2. [<id>] <requirement text>
        Similarity: <score as percentage>
        Reason: <short explanation>

        At the end add the hiring hint
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-5.1", messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content

        except Exception as e:
            return f"LLM error: {str(e)}"
