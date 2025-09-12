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
        "input_schema": t.get("input_schema", {"type": "object", "properties": {}, "required": []}),
    }
    for t in TOOLS_DEFINITION
]


async def beautify_response(raw_json: Any, user_query: str) -> str:
    if not raw_json:
        return f"No cars found for your request: '{user_query}'."

    total_items = len(raw_json)
    max_display = total_items if total_items <= 5 else 10 if total_items <= 20 else 15

    simplified = [
        {k: v for k, v in car.items() if k in ("make", "model", "year", "color", "price")}
        for car in raw_json
    ]
    display_data = simplified[:max_display]
    summary_text = f"...and {total_items - max_display} more." if total_items > max_display else ""
    json_string = json.dumps(display_data, separators=(',', ':'))

    system_prompt = f"""
You are a professional car assistant. Format the data for a non-technical user.
RULES:
1. Do not show IDs, UUIDs, timestamps, or technical fields.
2. Group cars by make and list their models with years.
3. Summarize long lists if necessary, but remain clear.
4. Write in plain natural sentences.
5. Include confirmations for added, updated, or deleted cars.
6. End with a short summary if applicable.
7. Do NOT include any caution or note about data accuracy.
8. If the list was truncated, include: "{summary_text}"
"""

    try:
        response = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=400,
            system=system_prompt,
            messages=[{"role": "user", "content": f"User query: {user_query}\n\nData: {json_string}"}],
        )
        formatted_text = "".join(
            getattr(b, "text", "") for b in response.content if getattr(b, "type", None) == "text"
        )
        return formatted_text.strip() or f"Found data, but could not format for: {user_query}"
    except Exception as e:
        logger.error(f"Error in beautify_response: {e}")
        return "Sorry, there was an error formatting the response."


async def run_agent(user_input: str) -> str:
    system_prompt = """
You are a professional car database assistant.
Always respond in plain language.
Confirm additions, updates, deletions.
Summarize long lists.
Do not include technical data like IDs, UUIDs, or timestamps.
Do NOT include any caution or note about data accuracy.
"""

    try:
        response = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=700,
            system=system_prompt,
            tools=TOOLS,
            messages=[{"role": "user", "content": user_input}],
        )

        agent_result, text_content = None, ""

        for block in response.content:
            block_type = getattr(block, "type", "")
            if block_type == "tool_use":
                tool_name, params = getattr(block, "name", ""), getattr(block, "input", {})
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

        return await beautify_response(agent_result, user_input) if agent_result is not None else text_content.strip() or "No results found."
    except Exception:
        logger.exception("Error in run_agent")
        return "Error processing the request."
