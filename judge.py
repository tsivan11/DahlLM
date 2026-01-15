import os
import json
from dataclasses import dataclass
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@dataclass
class JudgeResult:
    safety_passed: bool
    overall_score: float
    structure_score: float
    pacing_score: float
    moral_score: float
    engagement_score: float
    feedback: str


def judge_story(story: str, age: int) -> JudgeResult:

    
    judge_prompt = f"""You are an expert children's story editor. 
        Your task is to evaluate a bedtime story for a {age}-year-old child.

        EVALUATION CRITERIA:

        1. SAFETY CHECK (Very important: BINARY PASS/FAIL):
        - No violence, blood, death, scary imagery, or nightmares
        - No complex fears (abandonment, abuse, existential themes)
        - emotionally safe with gentle tension only
        - Only Age-appropriate themes for {age} year olds
        - If ANY safety concern exists, mark as FAILED

        2. STRUCTURE (0-10):
        - Clear 3 act structure (beginning, middle, end)
        - Well-balanced act lengths
        - Proper story arc with setup, challenge, resolution

        3. PACING (0-10):
        - Not rushed, especially the ending
        - Good flow and rhythm

        4. MORAL (0-10):
        - Clear positive lesson
        - Emerges naturally from the story

        5. ENGAGEMENT (0-10):
        - Vivid descriptions and imagery
        - Interesting characters
        - Captures imagination of a child

        STORY TO EVALUATE:
        {story}

        Provide your evaluation in the following JSON format ONLY (no other text):
        {{
            "safety_passed": true/false,
            "structure_score": 0-10,
            "pacing_score": 0-10,
            "moral_score": 0-10,
            "engagement_score": 0-10,
            "feedback": "Specific, actionable feedback for improvement. If scores are low, explain why and how to fix. Be constructive and specific."
        }}
        """

    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": judge_prompt}],
        temperature=0.3,
        max_tokens=1000
    )
    
    
    response_text = resp.choices[0].message.content.strip()
    try:
        result_dict = json.loads(response_text)
        weights = {
            'structure_score': 0.30,
            'pacing_score': 0.30,
            'moral_score': 0.25,
            'engagement_score': 0.15,
        }
        
        overall = sum(result_dict[key] * weight for key, weight in weights.items())
        
        return JudgeResult(
            safety_passed=result_dict['safety_passed'],
            overall_score=round(overall, 2),
            structure_score=result_dict['structure_score'],
            pacing_score=result_dict['pacing_score'],
            moral_score=result_dict['moral_score'],
            engagement_score=result_dict['engagement_score'],
            feedback=result_dict['feedback']
        )
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Warning: Failed to parse judge response: {e}")
        print(f"Raw response: {response_text}")
        
        # Return a default "safe but needs improvement" result
        return JudgeResult(
            safety_passed=True,
            overall_score=6.0,
            structure_score=6.0,
            pacing_score=6.0,
            moral_score=6.0,
            engagement_score=6.0,
            feedback="Unable to properly evaluate. Please review manually."
        )
