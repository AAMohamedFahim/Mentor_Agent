from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq


from dotenv import load_dotenv
import os


# load_dotenv()


# groq_api_key=os.environ['GROQ_API_KEY']
groq_api_key="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"




llm=ChatGroq(groq_api_key=groq_api_key,
             model_name="llama-3.1-8b-instant")
def mentor_ai_res(topic,user_id):

        prompt = ChatPromptTemplate.from_template(
         """
         you are a helpfull mentor ai to assist user related to there roadmap
         
         here is the road that user has:
         
         graph TD
    A[Data Science]:::hoverable --> B[Data Preprocessing]:::hoverable
    A --> C[Data Visualization]:::hoverable
    B --> D[Exploratory Data Analysis]:::hoverable
    C --> E[Data Storytelling]:::hoverable
    B --> F[Feature Engineering]:::hoverable
    D --> G[Data Quality Assurance]:::hoverable
    F --> H[Model Development]:::hoverable
    H --> I[Model Evaluation]:::hoverable
    E --> J[Business Insights]:::hoverable
    I --> K[Deployment and Maintenance]:::hoverablegraph TD
    A[Data Analysis]:::hoverable --> B[Data Collection]:::hoverable
    A --> C[Data Preprocessing]:::hoverable
    B --> D[Data Sources]:::hoverable
    B --> E[Data Extraction]:::hoverable
    C --> F[Data Cleaning]:::hoverable
    C --> G[Feature Engineering]:::hoverable
    D --> H[Primary Sources]:::hoverable
    D --> I[Secondary Sources]:::hoverable
    E --> J[Manual Data Collection]:::hoverable
    E --> K[Automated Data Collection]:::hoverable
    F --> L[Handling Missing Values]:::hoverable
    F --> M[Data Transformation]:::hoverable
    G --> N[Feature Selection]:::hoverable
    G --> O[Feature Creation]:::hoverable
    H --> P[Surveys]:::hoverable
    H --> Q[Social Media]:::hoverable
    I --> R[Books]:::hoverable
    I --> S[Research Papers]:::hoverable
    J --> T[Manual Entry]:::hoverable
    J --> U[Data Scraping]:::hoverable
    K --> V[API Integration]:::hoverable
    K --> W[Crawler]:::hoverable
         
         
         here is the user data : 
        Fahim, born on December 12, 2004, is a 19-year-old individual who has completed 12th grade. He is currently interested in the field of Data Science, aiming to become a data scientist. Despite not having any formal courses or practical projects in Data Science, he is determined to learn and grow in this field.
         
         Kamesh, born on December 12, 2004, is a 19-year-old data engineer. He has completed his 12th grade and is currently studying to become a big data analyst. Despite not having any formal courses or practical projects in Data Engineering, Kamesh is determined to learn and grow in this field.
         
         rule: 
            1. only reply to the question dont tell anything other then that.
            2. your reply should be short as much as possible.
         
         based on this data reply to this question:
         {input}.
 """)

        print(user_id)

       
        
        llm_chain = LLMChain(
                llm=llm,
                prompt=prompt)

        response =llm_chain.invoke({"input":topic})
        return response['text']

# topic="give me the roadmap for python" 
# print(response(topic))
           
                        
            
    
 
 


      