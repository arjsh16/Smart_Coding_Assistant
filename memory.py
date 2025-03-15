# This file contains the code for saving the old messages with their response in the memory of the AI Agent
store = []
def save_old_messages(query, output):
    store.append((query,output))
    return store
