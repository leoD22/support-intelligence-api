import json
from app.services.openai_client import get_openai_client
from app.services.ticket_tools import (
    GET_TICKET_HISTORY_TOOL,
    get_ticket_history
)


class InvalidToolArgumentsError(ValueError):
    pass


def ask_about_ticket(question: str):
    client = get_openai_client()

    response = client.responses.create(
        model="gpt-4o-mini",
        input=question,
        tools=[GET_TICKET_HISTORY_TOOL]
    )

    function_outputs = []

    for item in response.output:
        if item.type == "function_call":
            if item.name != "get_ticket_history":
                raise ValueError("Invalid function name")

            try:
                arguments = json.loads(item.arguments)

                if not isinstance(arguments, dict):
                    raise InvalidToolArgumentsError(
                        "Arguments must be an object"
                    )

                ticket_id = arguments["ticket_id"]
            except json.JSONDecodeError as e:
                raise InvalidToolArgumentsError(
                    "Invalid JSON arguments"
                ) from e
            except KeyError as e:
                raise InvalidToolArgumentsError(
                    "Missing ticket_id"
                ) from e

            if type(ticket_id) is not int or ticket_id <= 0:
                raise InvalidToolArgumentsError("Invalid ticket_id")
            tool_result = get_ticket_history(ticket_id)

            tool_output = json.dumps(tool_result, ensure_ascii=False)
            function_output = {
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": tool_output
            }

            function_outputs.append(function_output)

    if function_outputs:
        final_response = client.responses.create(
            model="gpt-4o-mini",
            previous_response_id=response.id,
            input=function_outputs
        )

        return final_response

    return response
