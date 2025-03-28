from openai import OpenAI
import os
from customizable_parameters import company_details, product_details, offers_available, additional_instructions
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

previous_response = ""
main_prompt = ""

def generate_greeting(customer_name):
    global main_prompt
    global previous_response

    greeting_prompt = f"""
    Generate a Twilio-compatible call script (IMPORTANT: Use only [A-Za-z0-1,.] characters in your response. The script should be 15 words max):

    You are convincing salesperson named Sarah that will not take no for an answer. You are have just cold called a potential customer. you are trying to sell them a product. 
    you are persuasive and you are very good at convincing people to buy your product. you are very good at making people feel comfortable and you are very good at
    making people feel like they can trust you.
    Here are the Company details: {company_details}
    Here are the Product details: {product_details}
    Here are the Offers available: {offers_available}
    Here are the Additional instructions: {additional_instructions}
    the customer name is: {customer_name}
    Here is a description of you and how you answer the phone:
    - Your name is Sarah
    - You are a salesperson
    - You are very persuasive
    - You are very good at convincing people to buy your product
    - Your Voice Tone is: sexy and confident

    Give me a greeting that you would say to the customer with a very short description of the product and give them an offer that you think they would be interested in. make your speech 15 words. focus on the product and how to sell it to the customer.
    at the end of your speech you should ask the customer the question if we can schedule an appointment to speak to a specialist. (IMPORTANT: Use only [a-z0-1,.] characters in your response. The script should be 15 words max. IMPORTANT: JUST GIVE THE SCRIPT NO NEED TO PRECEED IT WITH ANYTHING)
    (IMPORTANT: BE CONCISE AND TO THE POINT)
    ---------------------------------------------
    customer: Hello
    ---------------------------------------------
    you:
    """

    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a persuasive salesperson named Sarah."},
            {"role": "user", "content": greeting_prompt}
        ],
        max_tokens=70
    )

    previous_response = completion.choices[0].message.content
    main_prompt = greeting_prompt + previous_response + "\n---------------------------------------------\ncustomer:"

    print(previous_response)
    print("---------------------------------------------------")
    return previous_response

def continue_conversation(user_input):
    global main_prompt
    global previous_response

    main_prompt += user_input + "\n---------------------------------------------\nyou:"

    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a persuasive salesperson named Sarah."},
            {"role": "user", "content": main_prompt}
        ],
        max_tokens=70
    )

    previous_response = completion.choices[0].message.content
    main_prompt += previous_response + "\n---------------------------------------------\ncustomer:"
    print(previous_response)
    return previous_response