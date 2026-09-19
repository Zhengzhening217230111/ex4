## Import the necessary modules
## Import the function from the module parse_data
## Build your prompt based on the description the user provides 
## and the items that are available in the lost-and-found database.
## The model must follow the rules listed in the README file
## The function should return the system prompt and the user prompt.
## You may need to use json.dumps() to convert the available_items list into a JSON string.
import json
import ollama
# from ollama import chat
from parse_data import load_items, get_unclaimed_items, save_result
def build_prompt(description, available_items):
    system_prompt = """
You are campus lost‑and‑found matching assistant.
Rules you MUST strictly follow:
1. Only use items given in user input database.
2. Only return reasonably matching items, no unrelated items.
3. Not every detail needs to match for a possible match.
4. You MUST output ONLY valid JSON. No markdown, no ```, no explanation text.
JSON template:
{
    "matches": ["ITEM_ID"],
    "confidence": "LOW"
}
confidence values: HIGH / MEDIUM / LOW.
If no match: "matches": [], still include confidence key.
"""
    items_json = json.dumps(available_items, indent=2)
    user_prompt = f"""
Lost item user description: {description}
Available lost‑and‑found items:
{items_json}
Output ONLY pure JSON.
"""
    return system_prompt, user_prompt

## Logic to ask Qwen for all the possible matches based on the system prompt and user prompt.
## The function should return the response from Qwen.
def ask_qwen(system_prompt, user_prompt):
    resp = ollama.chat(
        model="qwen",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return resp["message"]["content"]
# resp.message.content

## Logic to parse the response from Qwen and return the result. 
## You may need to use json.loads() to convert the response string into a suitable Python data structure.
def parse_response(response_text):
    cleaned = response_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"matches": [], "confidence": "LOW"}

## Logic to validate the result returned by Qwen.
## It should check if the result is a dictionary, contains the keys "matches" and "confidence", and that the values are of the correct type.
## If everything is correct, then it should check if the item IDs in the "matches" list are valid IDs .
def validate_result(result, available_items):
    if not isinstance(result, dict):
        raise ValueError("Result must be dictionary")
    if "matches" not in result or "confidence" not in result:
        raise ValueError("Missing required keys: matches, confidence")
    if not isinstance(result["matches"], list):
        raise ValueError("matches must be list")
    if result["confidence"] not in ["LOW", "MEDIUM", "HIGH"]:
        raise ValueError("confidence must be LOW / MEDIUM / HIGH")
    valid_ids = {x["id"] for x in available_items}
    for match_id in result["matches"]:
        if match_id not in valid_ids:
            raise ValueError(f"Invalid item id {match_id}")
    return True

## Logic to display the matches found by Qwen in a user-friendly format.
## It should look something like this:
""" 
CAMPUS LOST-AND-FOUND ASSISTANT
==================================================
Describe the item you lost: I lost a black bag somewhere
Searching for possible matches...
MATCH RESULT
--------------------------------------------------
Confidence: MEDIUM
Possible matches:
ID: F101
Item: backpack
Color: black
Location: Library 2nd floor
Date found: 2026-09-15
Result saved to output/match_result.json
 """
## If no matches are found, it should display a message indicating that no matches were found, along with the empty list
def display_matches(result, available_items):
    print("CAMPUS LOST‑AND‑FOUND ASSISTANT")
    print("=" * 50)
    print("MATCH RESULT")
    print("-" * 50)
    print(f"Confidence: {result['confidence']}")
    match_ids = result["matches"]
    if len(match_ids) == 0:
        print("Possible matches: None (empty list)")
        return
    item_map = {i["id"]: i for i in available_items}
    for mid in match_ids:
        item = item_map[mid]
        print(f"ID: {item['id']}")
        print(f"Item: {item['item']}")
        print(f"Color: {item['color']}")
        print(f"Location: {item['location']}")
        print(f"Date found: {item['date']}")
    print("Result saved to output/match_result.json")

## Control center for the entire program.
def main():
    all_items = load_items("found_items.json")
    unclaimed = get_unclaimed_items(all_items)
    lost_description = input("Describe the item you lost: ")
    print("Searching for possible matches...")
    sys_prompt, user_prompt = build_prompt(lost_description, unclaimed)
    raw_response = ask_qwen(sys_prompt, user_prompt)
    parsed_result = parse_response(raw_response)
    try:
        validate_result(parsed_result, unclaimed)
    except ValueError:
        parsed_result = {"matches": [], "confidence": "LOW"}
    save_result(parsed_result, "output/match_result.json")
    display_matches(parsed_result, unclaimed)

if __name__ == "__main__":
    main()
