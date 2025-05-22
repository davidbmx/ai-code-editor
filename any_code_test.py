from any_code_graph import app

while True: 
    query = input("Enter your query: ")

    if query == "exit":
        break

    message = {
        "messages": [{"role": "user", "content": query,}],
    }

    for event in app.stream(message, config={"thread_id": "123"}, stream_mode="updates"):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)
