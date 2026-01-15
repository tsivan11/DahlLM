import os
from openai import OpenAI
from dotenv import load_dotenv
from judge import JudgeResult, judge_story

# load theAPI key
load_dotenv()

"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

A. If I had more time, a few changes I'd consider adding are:
1. The ability to pick from a variety of author writing styles 
(e.g. stories written in the style of this application's namesake Roald Dahl, or maybe Dr. Seuss)
2. I'd spend a lot more time testing and versioning prompts.
3. Langchain for better orchestration, retiries, complexity?
4. A means to store stories that have already been written, if the user wants to revist them.
"""


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # initializing it once

def write_story(age: str, story_request: str, previous_story: str = None, judge_feedback: str = None, max_tokens=4000, temperature=0.5) -> str:

    system_prompt = f"""You are DahlLM, a friendly and imaginative AI storyteller designed to create engaging and **age-appropriate** bedtime stories for children aged 5 to 10. 
    Your Goals:
    1. Write a warm, imaginative, calming bedtime story.
    2. Whatever the story topic is, ensure it is **age-appropriate** and emotionally safe with gentle tension and positive resolutions.
    3. Use simple, clear language that  is easy to understand but also rich in imagination.
    4. Keep the story length suitable for a bedtime story, and have distinct story arcs with a beginning, middle, and end

    Requirements:
    1. Protagonist is exactly {age} years old.
    2. The protagonist should have a name.
    3. The visual scenes should be clearly described.
    4. Include friendly supporting characters.
    5. The story should have a positive moral or lesson. The moral should be clear from the protagonist's journey. Do not state that it is a moral, explicitly.
    6. Avoid any content that could be inappropriate for children in this age group..
    7. Try to keep the different story arcs balanced in length. Do not rush the ending.
    8. The story length should be around 800-1200 words.
    9. There should be some challenge to overcome, but nothing too intense.

    Format:
    - Tale: [Story Title]
    - Begin with: Once upon a time...
    - Separate the arcs with paragraph breaks. Don't explicitly label the arcs.
    - Conclude with a pithy moral, and wish the child goodnight at the end. Do not mention "moral" explicitly.
    """

    
    if previous_story and judge_feedback:
        user_prompt = f"""
    You previously wrote this story:
    {previous_story}
    An editor has provided this feedback:
    {judge_feedback}
    
    Please revise the story based on this feedback while maintaining the core request: {story_request}
    Follow the system instructions carefully. Only return the improved story for the child to read.
    """
        

    else:
        user_prompt = f"""
    Narrate a bedtime story for a {age} year old child. The story should be about: {story_request}. If the topic is a typo, make your best guess at what the child meant.
    Follow the system instructions carefully. Before narration, plan the 3-act structure carefully. Do NOT display the plan, only the story for the child to read.
    """

    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=False,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content


def story_pipeline(age: int, story_request: str, quality_threshold: float = 7.5, max_iterations: int = 2) -> str:
    best_story = None
    best_score = 0.0
    
    for iteration in range(max_iterations):
        
        if iteration == 0:
            story = write_story(str(age), story_request)
        else:
            story = write_story(str(age), story_request, previous_story=best_story, judge_feedback=judge_result.feedback)
        
        
        # print("\nReviewing your story's quality.")
        judge_result = judge_story(story, age)
        
        #### Safety gate
        if not judge_result.safety_passed:
            #print("\nSafety check failed. Regenerating...")
            continue
        
        if judge_result.overall_score > best_score:
            best_story = story
            best_score = judge_result.overall_score
        
        
        if judge_result.overall_score >= quality_threshold:
            # print(f"\nStory approved. (Quality score: {judge_result.overall_score}/10)")
            return story
        else:
            pass
            # print(f"\nScore: {judge_result.overall_score}/10 - Working on improvements...")
    
    
    if best_story:
        print(f"\n Returning best version (Quality score: {best_score}/10)")
        return best_story
    else:
        print("\n Unable to generate safe story. Please try a different request.")
        return "I wasn't able to find a suitable story for that request. Please try again with a different idea!"


def main():
    
    while True:
        user_input_age = input("\nHello there, young one! My name is DahlLM, and I'm here to tell you a story. " \
                               "First, tell me, how old are you? ")
        try:
            age = int(user_input_age)
            if 5 <= age <= 10:
                break
            elif age < 5:
                print("You're a bit too young for my stories. Please come back when you're between 5 and 10!")
            else:
                print("I'm afraid you're a bit too old for my stories. Please come back later when I have some age-appropriate stories for you!")
        except ValueError:
            print("Please enter your age in numbers!")
    
    
    while True:
        user_input_request = input("What kind of story do you want to hear? ")
        if user_input_request.strip():
            break
        else:
            print("Please tell me what kind of story you'd like!")
    
    print("\nLet me check my library. I think I have just the story for you...")
    response = story_pipeline(age, user_input_request)
    
    print("\n" + "="*70)
    print(response)
    print("="*70)


if __name__ == "__main__":
    main()