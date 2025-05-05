# order_support_chatbot.py

import openai
import gradio as gr
import json

# Set your OpenAI API key
client = openai.OpenAI(api_key="sk-your-api-key-here")

# Mock function for checking order status
def get_order_status(order_id):
    orders = {
        "12345": "Your order 12345 has been shipped and will arrive in 2 days.",
        "67890": "Order 67890 is being processed and will ship tomorrow.",
        "11111": "Order 11111 was delivered on May 1st."
    }
    return orders.get(order_id, "Sorry, we couldn't find that order ID.")

# Chat function with GPT and function calling
def chat_with_gpt(message, history):
    messages = [{"role": "system", "content": "You are a helpful support assistant."}]
    for user_msg, bot_reply in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_reply})
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        functions=[
            {
                "name": "get_order_status",
                "description": "Check order status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "The order ID"
                        }
                    },
                    "required": ["order_id"]
                }
            }
        ],
        function_call="auto"
    )

    msg = response.choices[0].message
    if msg.function_call:
        args = json.loads(msg.function_call.arguments)
        order_id = args.get("order_id", "")
        result = get_order_status(order_id)
        history.append((message, result))
        return "", history
    else:
        bot_reply = msg.content
        history.append((message, bot_reply))
        return "", history

# Launch Gradio app
with gr.Blocks() as demo:
    gr.Markdown("## Order Support Chatbot")
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="Ask about your order:")
    state = gr.State([])
    msg.submit(chat_with_gpt, [msg, state], [msg, chatbot, state])

demo.launch()
