from dotenv import load_dotenv
from fastapi import FastAPI , HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error
import os
import redis
import pickle
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.schema import HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
import webbrowser
from flow import flow_generator
from typing import Dict
from mentor_ai import mentor_ai_res

load_dotenv()
app = FastAPI()


# UI MIDDLEWARES-------------------------------------------------------

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Enable CORS to allow requimport pickleests from other origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods, including POST
    allow_headers=["*"],  # Allows all headers
)




# Database connection configuration-------------------------------------
DB_CONFIG = {
    'host': 'localhost',
    'user': 'fahim',
    'password': '12112',
    'database': 'AI_Mentor'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

#USERID and NAME EXTRACTOR-----------------------------------------------------
user_id = ""
user_name = ""
def get_user_id_by_username(username: str) -> str:
    connection = None
    try:
        connection = get_db_connection()  # Assume this function exists to create a DB connection
        if not connection:
            raise Exception("Database connection error")

        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT user_id FROM user_table WHERE user_name = %s"
        cursor.execute(query, (username,))
        
        result = cursor.fetchone()
        
        if result:
            return result['user_id']
        else:
            return None

    except Error as e:
        print(f"Error: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            
            
def get_username_by_email(email: str) -> str:
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            raise Exception("Database connection error")

        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT user_name FROM user_table WHERE mail_id = %s"
        cursor.execute(query, (email,))
        
        result = cursor.fetchone()
        
        if result:
            return result['user_name']
        else:
            return None

    except Error as e:
        print(f"Error: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()





# Pydantic models----------------------------------------------------------
class UserSignUp(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str
    
class ChatInput(BaseModel):
    user_id: str
    message: str

class MentorInput(BaseModel):
    message: str
    

flowchart_storage: Dict[str, str] = {}
class FlowchartRequest(BaseModel):
    topic: str
    
#Data extractor-----------------------------------------------------
redis_client = redis.Redis(host='localhost', port=6379, db=0)

class ChatInput(BaseModel):
    user_id: str
    message: str

groq_api_key = "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"

def get_conversation_memory(user_id: str):
    """Retrieve the conversation memory for a specific user from Redis."""
    memory_data = redis_client.get(user_id)
    if memory_data is None:
        memory = ConversationBufferMemory(memory_key="history", return_messages=True)
    else:
        memory = pickle.loads(memory_data)
    return memory

def save_conversation_memory(user_id: str, memory):
    """Save the updated conversation memory for a user in Redis."""
    redis_client.set(user_id, pickle.dumps(memory))
    
def extract_user_convo(user_id):
    
        def conversation_to_string(memory):
            conversation = ""
            for message in memory.chat_memory.messages:
                if isinstance(message, HumanMessage):
                    conversation += f"Human: {message.content}\n"
                elif isinstance(message, AIMessage):
                    conversation += f"AI: {message.content}\n"
            return conversation.strip()
        r = redis.Redis(host='localhost', port=6379, db=0)

        serialized_data = r.get(user_id)

        if serialized_data:
            data = pickle.loads(serialized_data)
            # print(type(data))
            str_data = conversation_to_string(data)
            print(str_data)
        else:
            print("No data found for 'user1'")
            
        return str_data
    
def bio_summarizer(history_string):
        llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-groq-70b-8192-tool-use-preview")

        prompt_template = """
            summarize the below user convertation and give me only user data as biography paragraph.
            
            note:
            1. mention all information clearly.
            2. dont add additional information and make sure to add all information
            
            convertation:
            {history_string}
            """

        prompt = PromptTemplate.from_template(template=prompt_template)

        chain = LLMChain(llm=llm, prompt=prompt)


        op = chain.run({"history_string": history_string})
        file_name = user_id + "_about"
        try:
            with open(file_name, 'w') as file:  
                file.write(op)
            print(f"Data written to {file_name}")
        except Exception as e:
            print(f"An error occurred: {e}")
        return(op)

#TOOLCALL---------------------------------------------------

def process_tool_call(response: str):
    if "<tool_call>" in response and "</tool_call>" in response:
        tool_call_start = response.index("<tool_call>")
        tool_call_end = response.index("</tool_call>") + len("</tool_call>")
        tool_call_string = response[tool_call_start:tool_call_end]
        
        # Extract JSON from tool call
        json_str = tool_call_string.replace("<tool_call>", "").replace("</tool_call>", "").strip()
        try:
            tool_call = json.loads(json_str)
            if tool_call.get("name") == "generateResponse":
                user_message = tool_call.get("arguments", {}).get("userMessage")
                if user_message:
                    # Here, instead of generating a new response, we'll return the user message
                    # as it's already the AI's response to the user
                    return user_message
        except json.JSONDecodeError:
            print("Invalid JSON in tool call")
    
    # If no valid tool call is found, return the original response
    return response


#-----------------------------------------------------
    
# ENDPOINTS --------------------------------------------------------------------

@app.post("/signup")
async def signup(user: UserSignUp):
    global user_id
    global user_name
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection error")

    try:
        cursor = connection.cursor()

        # Check if the username already exists
        cursor.execute("SELECT * FROM user_table WHERE user_name = %s", (user.name,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already exists")

        # Check if the email already exists
        cursor.execute("SELECT * FROM user_table WHERE mail_id = %s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already exists")

        # Insert the new user
        insert_query = "INSERT INTO user_table (user_name, mail_id, password_) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (user.name, user.email, user.password))
        connection.commit()
        
        user_id = get_user_id_by_username(user.name)
        user_name = user.name
        
        print("\n\n\n\n",user_id,user_name)

        return {"message": "User registered successfully"}

    except mysql.connector.Error as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Error during registration: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            
            
@app.post("/login")
async def login(user: UserLogin):
    global user_id
    global user_name
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection error")

    try:
        cursor = connection.cursor(dictionary=True)

        select_query = "SELECT * FROM user_table WHERE mail_id = %s"
        cursor.execute(select_query, (user.email,))
        user_data = cursor.fetchone()

        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")

        if user_data['password_'] != user.password:
            raise HTTPException(status_code=401, detail="Incorrect password")
        
        user_name = get_username_by_email(user.email)
        user_id = get_user_id_by_username(user_name)
        
        user_name = user_name
        
        print("\n\n\n\n",user_id,user_name)



        return {"message": "Login successful"}

    except mysql.connector.Error as e:
        raise HTTPException(status_code=400, detail=f"Error during login: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            
            
@app.post("/chat")
async def chat(chat_input: ChatInput):
    # user_id = chat_input.user_id
    user_message = chat_input.message
    status = False
    
    
    memory = get_conversation_memory(user_id)

    llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-70b-versatile")

    prompt_template = """you are a helpfull assistant to ask questions from user
    You will ask the following questions to gather the necessary information:
        1. name.
        2. birthday.(this is oct 2024 if user provides year and there age below 10 years then make sure there name)
            Note :  if they wont provide year then dont calculate age
        3. highest level of education completed so far
        4. current field or area of study
        5. check does user taken any formal courses in this area
        6. does user done any projects or practical work in there field
        7. check what is users aim.
        8. What tends user to slow down there learning process.
        
        note:
            1.your tone should be polite and friendly and more humanastic
            2.respose like a convertation. it should be short and easy to read.
            3.your reply should be short.
            4. your reply should be under 15 words.
            5. dont assist anything else then asking question.
            
        
        rules:
        
        1. you must ask questions one by one.
        2. dont ask question if already user given.
        3. if user cant understand question then try to explain in short and simple.
        4. once you get all neccasary details Please respond with the exact phrase: 'Thank you for providing your details!' or 'Thank you for providing your details!' (with an exclamation mark).
        5. if user cant reply related to question try to explain that question where user can get easily.
        6. dont always tell about previous question.
        7. check does user answer is realistic or not then only you should move to nest question.
        8. you should never ask same question again for any reason.
        9. dont be ask follow up questions

        
        Here is the conversation history:
        {history}

    Now, the user has asked the following question:
    {human_input}
    """

    prompt = PromptTemplate(template=prompt_template, input_variables=["history", "human_input"])

    chain = LLMChain(llm=llm, prompt=prompt, memory=memory)
    response = chain.predict(human_input=user_message)
    
    processed_response = process_tool_call(response)


    save_conversation_memory(user_id, memory)
    # print(response)
    history_string = extract_user_convo(user_id)
    print(history_string)
    if "Thank you for providing your detail" in processed_response:
        print("\n\n\n---------------------------------------------------",type(history_string))
        response1 = bio_summarizer(history_string)
    return {"response": processed_response}



@app.post("/profile")
async def chat():
    global user_name
    print(user_name)
    return {
    "name": user_name,
    "role": "Web Developer | AI Enthusiast",
    "progress": 85,
    "courses": 12,
    "rating": 4.8
    }
    
# Generate Flowchart route
@app.post("/api/generateFlowchart")
async def generate_flowchart(req: FlowchartRequest):
    global user_id
    topic = req.topic
    print("topic: ", topic)
    
    # Check if the topic already exists in storage
    if topic in flowchart_storage:
        return {
            "status": "success",
            "mermaid_code": flowchart_storage[topic],
            "message": "Fetched existing flowchart"
        }

    # Generate new flowchart
    try:
        new_mermaid_code = flow_generator(topic)
        # file_name_flow = user_id + "_flows"
        # # Open the file in append mode ('a') which creates the file if it doesn't exist
        # with open(file_name_flow, 'a') as file:
        #     file.write(new_mermaid_code)  # Append the code content with a newline for clarity
        # print(f"Code has been appended to {file_name}")
        
    
    #     new_mermaid_code = '''graph TD
    # A[Python Programming]:::hoverable --> B[Basic Syntax and Data Types]
    # A --> C[Control Structures and Functions]
    # B --> D[Variables and Data Types]
    # B --> E[Operators and Expressions]
    # C --> F[Conditional Statements]
    # C --> G[Loops and Iterations]
    # F --> H[If-Else Statements]
    # G --> I[For Loops]
    # D --> J[Lists and Tuples]
    # E --> K[Arithmetic and Comparison Operators]
    # J --> L[List Methods]
    # I --> M[While Loops]
    # H --> N[Switch Statements]
    # B --> O[Error Handling]
    # O --> P[Try-Except Blocks]
    # K --> Q[Logical Operators]
    # L --> R[Sorting and Searching]
    # G --> S[Break and Continue Statements]
    # E --> T[Mathematical Operations]
    # T --> U[Trigonometric Functions]
    # F --> V[Decision Making]
    # R --> W[Array and Dictionary Operations]
    # S --> X[Exception Handling]
    # C --> Y[Module and Package Importing]
    # Y --> Z[Importing Modules]
    # Z --> AA[Importing Specific Functions]
    # AA --> BB[Exporting Functions]
    # BB --> CC[Class and Object-Oriented Programming]
    # CC --> DD[Encapsulation and Abstraction]
    # DD --> EE[Inheritance and Polymorphism]
    # EE --> FF[Operator Overloading]'''
        
        # Store the generated code
        flowchart_storage[topic] = new_mermaid_code
        status = f'<p>Average time to complete {topic}: 2 hours</p><p>Status: <input type="radio" name="status" value="Not Touched"> Not Touched<input type="radio" name="status" value="In Progress"> In Progress <input type="radio" name="status" value="Completed"> Completed </p>'
        print("\n\n\n\n\n1221")
        return {
            "status": "success",
            "topic": topic,
            "progeress": status,
            "mermaid_code": new_mermaid_code,
            "message": "Generated new flowchart"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating flowchart: {str(e)}")

# Delete a flowchart by topic
@app.delete("/api/deleteFlowchart")
async def delete_flowchart(topic: str):
    if topic not in flowchart_storage:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Remove the topic from storage
    del flowchart_storage[topic]
    return {"status": "success", "message": f"Deleted flowchart for {topic}"}

# Delete all flowcharts
@app.delete("/api/deleteAllFlowcharts")
async def delete_all_flowcharts():
    flowchart_storage.clear()  # Clears the entire storage
    return {"status": "success", "message": "Deleted all flowcharts"}

# Get all stored topics
@app.get("/api/getAllTopics")
async def get_all_topics():
    return {"topics": list(flowchart_storage.keys())}

@app.post("/api/chatbot")
async def generate_flowchart(mentor: MentorInput):
    global user_id
    print("\n\n\n\n",user_id)
    response = mentor_ai_res(mentor.message,user_id)
    return({'response':response,"status":"success"})
    



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    time.sleep(2)
    
    # Automatically open the front-end in the browser
    webbrowser.open_new("http://0.0.0.0:8000/static/loginpage/log_sign.html")

