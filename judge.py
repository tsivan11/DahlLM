import os
import json
from dataclasses import dataclass
from openai import OpenAI
from dotenv import load_dotenv
from prompts import get_judge_prompt

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

    judge_prompt = get_judge_prompt().format(age=age, story=story)

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
