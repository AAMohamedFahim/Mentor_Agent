from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq


from dotenv import load_dotenv
import os


# load_dotenv()


# groq_api_key=os.environ['GROQ_API_KEY']
groq_api_key="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"

prompt = ChatPromptTemplate.from_template(
         """
You are an expert at creating detailed learning roadmaps in Mermaid syntax.
Based on the user's request, identify the key learning areas.
mermaid syntax rule :
        1) Each topic name must  be represented as a node in the format of  A[Topic name]:::hoverable.
        2) Use this  arrows (-->) to show relationships and progression between nodes.
        3) Add interactivity to each node by applying the :::hoverable attribute.
        4) Subtopics must be connected to their parent topics logically donot miss match the flow.
        5) you should provide an organized structure with appropriate labels.
        6) Use the following  format for generating the mermaid flow:
                 graph TD
                 A[Main Topic]:::hoverable --> B[Subtopic 1]:::hoverable
                 A --> C[Subtopic 2]:::hoverable
                 B --> D[Sub-subtopic 1]:::hoverable
        7) you must complete the flow in proper mermaid format.
output format:
   You will must obey the below format to generate the output.
   1) you must only give me the mermaid flow chart with correct order.
   2) anyother ouput are resticted.
   3) do not give any prefaces and conclusion while generating the output. 
Rules :
 1) you should Only  give Mermaid-formatted flowcharts
 2) Any other type of response is restricted.
 3) you never should give the human readable format as an output.
 4) you must complete the flow in proper mermaid format avoid deviation.
 5) the output must be consistent with the mermaid syntax rule.
 6) Stick to this rules and avoid deviations.         
now generate the  Mermaid-formatted flowchart with the user query as follows  {input}.
 """)


llm=ChatGroq(groq_api_key=groq_api_key,
             model_name="llama-3.1-8b-instant")
def flow_generator(topic):
        llm_chain = LLMChain(
                llm=llm,
                prompt=prompt)

        response =llm_chain.invoke({"input":topic})
        return response['text']

# topic="give me the roadmap for python" 
# print(response(topic))
           
                        
            
    
 
 


      