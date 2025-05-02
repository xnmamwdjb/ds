class Message_list:

    def __init__(self, system_prompt="You are a helpful assistant."):
        system_message = {"role": "system", "content": system_prompt}
        self.message_list = [system_message,]

    def append_message(self, role, content):
        message = {"role": role, "content": content}
        self.message_list.append(message)

    def show_list(self):
        for message in self.message_list:
            print(message["role"], ":\n", message["content"], "\n")

    def show_last_message(self):
        message = self.message_list[-1]
        print(message["role"], ":\n", message["content"], "\n")
