import os
import logging
import json
from dotenv import load_dotenv
import anthropic
from typing import Any
from agents.tools_definition import TOOLS_DEFINITION

# --- Setup ---
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

TOOLS: Any = [
    {
        "name": t["name"],
        "description": t["description"],
        "input_schema": t.get("input_schema") or {
            "type": "object", "properties": {}, "required": []
        },
    }
    for t in TOOLS_DEFINITION
]

async def beautify_response(raw_json_data: Any, user_query: str) -> str:
    """
    Formats raw tool output into user-friendly text.
    Summarizes long lists and shows only relevant fields.
    """
    if not raw_json_data:
        return f"No cars found for your request: '{user_query}'."

    # Only keep relevant fields
    simplified_data = [
        {k: v for k, v in car.items() if k in ("make", "model", "year", "color", "price")}
        for car in raw_json_data
    ]

    # Summarize long lists
    MAX_DISPLAY = 10
    display_data = simplified_data[:MAX_DISPLAY]
    summary_text = f"...and {len(simplified_data) - MAX_DISPLAY} more." if len(simplified_data) > MAX_DISPLAY else ""

    json_string = json.dumps(display_data, separators=(',', ':'))

    system_prompt = f"""
You are a professional car assistant. Format the data for a non-technical user.
RULES:
1. Do not show IDs, UUIDs, timestamps, or technical fields.
2. Group cars by make and list their models with years.
3. Summarize long lists if necessary, but remain clear.
4. Write in plain natural sentences that a normal customer can understand.
5. Include confirmations for added, updated, or deleted cars.
6. End with a short summary if applicable.
7. Do NOT include any caution or note about data accuracy.
8. If the list was truncated, include: "{summary_text}"
"""

    try:
        response = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=400,  # optimized for speed
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": f"User query: {user_query}\n\nData: {json_string}"
            }],
        )

        formatted_text = "".join(
            getattr(block, "text", "")
            for block in response.content
            if getattr(block, "type", None) == "text"
        )

        return formatted_text.strip() if formatted_text else f"Found data, but could not format for: {user_query}"

    except Exception as e:
        logger.error(f"Error in beautify_response: {e}")
        return "Sorry, there was an error formatting the response."

async def run_agent(user_input: str) -> str:
    """
    Main agent runner: selects the tool or returns direct text,
    then beautifies the output for end users.
    """
    system_prompt = """
You are a professional car database assistant.
Always respond in plain language.
Confirm additions, updates, deletions.
Summarize long lists.
Do not include technical data like IDs, UUIDs, or timestamps.
Do NOT include any caution or note about data accuracy.
"""

    try:
        # Ask LLM to decide tool or generate text directly
        response = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=700,  # optimized for speed and clarity
            system=system_prompt,
            tools=TOOLS,
            messages=[{"role": "user", "content": user_input}],
        )

        agent_result: Any = None
        text_content = ""

        for block in response.content:
            block_type = getattr(block, "type", "")
            if block_type == "tool_use":
                tool_name = getattr(block, "name", "")
                params = getattr(block, "input", {})
                logger.info(f"Calling tool: {tool_name} with params: {params}")

                try:
                    tool_func = next(t["function"] for t in TOOLS_DEFINITION if t["name"] == tool_name)
                    agent_result = await tool_func(**params)
                    break
                except StopIteration:
                    agent_result = f"Error: Tool '{tool_name}' not found."
                    break
                except Exception as e:
                    logger.error(f"Error executing tool '{tool_name}': {e}")
                    agent_result = f"Error: Failed to execute tool '{tool_name}'."
                    break
            elif block_type == "text":
                text_content += getattr(block, "text", "")

        if agent_result is not None:
            return await beautify_response(agent_result, user_input)

        if text_content:
            return text_content.strip()

        return "No results found."

    except Exception:
        logger.exception("Error in run_agent")
        return "Error processing the request."
