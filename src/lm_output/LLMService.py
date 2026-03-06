import os

from openai import OpenAI


class LLMService:
    def __init__(self):

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key or api_key.strip() == "":
            raise RuntimeError(
                "\n\n[LLM disabled] No OPENAI_API_KEY configured.\n"
                "To use the LLM variant set the environment variable:\n\n"
                "export OPENAI_API_KEY=<your_api_key>\n"
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

        Each requirement has the following structure:
        id | requirement_text | similarity_score

        Task:
        1. Identify the requirements that are most similar to the user requirement.
        2. Present the similar requirements as a list.
        3. For each requirement include:
        - similarity
        - id
        - text

        After the list, explain why these requirements are similar.

        Output format:

        Similar Requirements:
        1. similarity: <score> | id: <id> | text: <requirement text>
        2. similarity: <score> | id: <id> | text: <requirement text>

        Explanation:
        Explain why these requirements are semantically similar.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content

        except Exception as e:
            return f"LLM error: {str(e)}"
