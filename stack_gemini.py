
from details import *
import google.generativeai as genai
from stackapi import StackAPI
import requests
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import html

# Set up Stack API
SITE = StackAPI('stackoverflow')
def get_stack_exchange_data(query, site=SITE):
    try:
        results = site.fetch('search', intitle=query)
        
        if results['items']:
            top_result = results['items'][0]
            question_id = top_result['question_id']
            
            answers = site.fetch('questions/{}/answers'.format(question_id), filter='withbody')
            
            if answers['items']:
                sorted_answers = sorted(answers['items'], key=lambda x: x.get('score', 0), reverse=True)
                top_answer = sorted_answers[0]['body']
                
                code_blocks = re.findall(r'<pre><code>(.*?)</code></pre>', top_answer, re.DOTALL)
                
                if not code_blocks:
                    code_blocks = re.findall(r'<code>(.*?)</code>', top_answer, re.DOTALL)
                
                if not code_blocks:
                    code_blocks = re.findall(r'(?:<pre>)?(?:<code.*?>)(.*?)(?:</code>)(?:</pre>)?', top_answer, re.DOTALL)
                
                if code_blocks:
                    stack_output = f"Solution from Stack Overflow (Question: {top_result['title']}):\n\n"
                    for block in code_blocks:
                        clean_code = html.unescape(block)
                        clean_code = re.sub(r'<.*?>', '', clean_code)
                        stack_output += f"{clean_code}\n\n"
                    return stack_output
                else:
                    clean_answer = re.sub(r'<.*?>', ' ', top_answer)
                    clean_answer = html.unescape(clean_answer)
                    clean_answer = re.sub(r'\s+', ' ', clean_answer).strip()
                    return f"Answer from Stack Overflow (Question: {top_result['title']}):\n\n{clean_answer}"
            else:
                return f"No answers found for question: {top_result['title']}"
        return "Nothing relevant on Stack Overflow. Sorry!"
    except requests.exceptions.RequestException as e:
        print(f"Oops, something went wrong: {e}")
        return None

def compare_relevancy(stack_data, gemini_data, query):
    if not stack_data or "Nothing relevant" in stack_data:
        return gemini_data
    
    if not gemini_data or "Error:" in gemini_data:
        return stack_data
    
    vectorizer = TfidfVectorizer().fit_transform([query, stack_data, gemini_data])
    vectors = vectorizer.toarray()
    
    query_vec = vectors[0].reshape(1, -1)
    stack_vec = vectors[1].reshape(1, -1)
    gemini_vec = vectors[2].reshape(1, -1)
    
    stack_similarity = cosine_similarity(query_vec, stack_vec)[0][0]
    gemini_similarity = cosine_similarity(query_vec, gemini_vec)[0][0]
    
    if stack_similarity > gemini_similarity:
        return stack_data
    return gemini_data

# This is what we tell Gemini & Stack Exchange
context = '''
You are an AI assistant that provides concise and effective responses. Follow these rules:

1. Analyze the user's request and determine if it requires new code or an explanation.
2. If the request involves writing new code, use Gemini, Stack Overflow, and relevant sources.
3. If the request does NOT require new code, reference Gemini data and previous messages if necessary.
4. Provide a short, precise summary before the solution.
5. If code is needed, use an appropriate format(give a python code, unless mentioned otherwise):
   - If a function is suitable:
     ```
     def users_request(parameters):
         # Function code
         return output
     ```
     Time Complexity: O(...)
     Space Complexity: O(...)
   - Otherwise, provide a relevant snippet.
6. If no direct answer is found, suggest alternative approaches or best practices.
'''

def main(prompt):
    try:
        genai.configure(api_key=pwd.gemini())
        model = genai.GenerativeModel("gemini-2.0-flash")

        try:
            response = model.generate_content(context + prompt)
            generated_text = response.text
        except Exception as e:
            generated_text = f"Error: {e}"
    except Exception as e:
        generated_text = f"Error connecting to Gemini: {e}"

    stack_data = get_stack_exchange_data(prompt)
    
    final_output = compare_relevancy(stack_data, generated_text, prompt)
    
    return final_output
