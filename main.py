import os
from openai import OpenAI
from dotenv import load_dotenv

# load theAPI key
load_dotenv()

"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

A. If I had more time, a few changes I'd consider adding are:
1. The ability to pick from a variety of author writing styles 
(e.g. stories written in the style of this application's namesake Roald Dahl, or maybe Dr. Seuss)
2. 
"""


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # initializing it once
def call_model(age: str, story_request: str, max_tokens=3000, temperature=0.4 ) -> str: # experimented  with temperature values to balance creativity and safety

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

    Format:
    - Title: [Story Title]
    - Begin with: Once upon a time...
    - Separate the arcs with paragraph breaks.
    - Conclude with a pithy moral, and wish the child goodnight at the end.
    """

    
    user_prompt = f"""
    Narrate a bedtime story for a {age} year old child. The story should be about: {story_request}.
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
    
    print("\nLet me search my library, I think I have just the story...\n")
    response = call_model(str(age), user_input_request)
    print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
    print(response)


if __name__ == "__main__":
    main()