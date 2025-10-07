import json
import pandas as pd
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

load_dotenv()

def validate_patient(message: str) -> str:
    """
    Function used to register and validate patients info

    Args:
        message: the message sent by the user
    """

    try:
        patient_json = json.loads(str(message).replace('\'', '\"'))

        patients_df = pd.read_csv('data/patients_info.csv')
        df_columns = patients_df.columns
        register_df = pd.DataFrame([[patient_json[df_columns[0]], patient_json[df_columns[1]], patient_json[df_columns[2]]]], columns=df_columns)
        
        patients_df = pd.concat([patients_df, register_df]).drop_duplicates(keep='first')
        patients_df.to_csv('data/patients_info.csv', index=False)

        return 'Success'
        
    except Exception as e:
        print(message)
        print(e)
        return 'Error'

def new_appointment(message: str) -> str:
    """
    This agent is used to answer the question using data from a patients dataset. 

    Args:
        message: the message sent by the user
    """

    try:
        appointment_json = json.loads(str(message).replace('\'', '\"'))

        appointment_df = pd.read_csv('data/appointments_info.csv')
        df_columns = appointment_df.columns
        register_df = pd.DataFrame([[appointment_json[df_columns[0]], appointment_json[df_columns[1]], appointment_json[df_columns[2]], appointment_json[df_columns[3]], "scheduled"]], columns=df_columns)
        
        appointment_df = pd.concat([appointment_df, register_df]).drop_duplicates(keep='last')
        appointment_df.to_csv('data/appointments_info.csv', index=False)

        return 'Success'
        
    except Exception as e:
        print(message)
        print(e)
        return 'Error'

def list_appointment(message: str) -> str:
    """
    This agent is used to answer the question using data from a patients dataset. 

    Args:
        message: the message sent by the user
    """

    try:
        appointment_json = json.loads(str(message).replace('\'', '\"'))

        appointment_df = pd.read_csv('data/appointments_info.csv')
        appointment_df = appointment_df[appointment_df.patient_name == appointment_json['patient_name']]

        return appointment_df.to_dict('records')
        
    except Exception as e:
        print(message)
        print(e)
        return 'Error'
    
def confirm_appointment(message: str) -> str:
    """
    This agent is used to answer the question using data from a patients dataset. 

    Args:
        message: the message sent by the user
    """

    try:
        appointment_json = json.loads(str(message).replace('\'', '\"'))

        appointment_df = pd.read_csv('data/appointments_info.csv')
        df_columns = appointment_df.columns
        register_df = pd.DataFrame([[appointment_json[df_columns[0]], appointment_json[df_columns[1]], appointment_json[df_columns[2]], appointment_json[df_columns[3]], "confirmed"]], columns=df_columns)
        
        appointment_df = pd.concat([appointment_df, register_df]).drop_duplicates(keep='last', subset=['patient_name', 'doctor_name', 'date', 'time'])
        appointment_df.to_csv('data/appointments_info.csv', index=False)

        return 'Success'
        
    except Exception as e:
        print(message)
        print(e)
        return 'Error'
    
def cancel_appointment(message: str) -> str:
    """
    This agent is used to answer the question using data from a patients dataset. 

    Args:
        message: the message sent by the user
    """

    try:
        appointment_json = json.loads(str(message).replace('\'', '\"'))

        appointment_df = pd.read_csv('data/appointments_info.csv')
        df_columns = appointment_df.columns
        register_df = pd.DataFrame([[appointment_json[df_columns[0]], appointment_json[df_columns[1]], appointment_json[df_columns[2]], appointment_json[df_columns[3]], "canceled"]], columns=df_columns)
        
        appointment_df = pd.concat([appointment_df, register_df]).drop_duplicates(keep=False, subset=['patient_name', 'doctor_name', 'date', 'time'])
        appointment_df.to_csv('data/appointments_info.csv', index=False)

        return 'Success'
        
    except Exception as e:
        print(message)
        print(e)
        return 'Error'
    
class MedicalAgent:
    """
    A class to create and manage a ReAct agent with multiple medical appointment tools.
    """

    _SYSTEM_PROMPT = """
    You are an assistant for medical appointment. 
    When a new conversation begins, the first step might be to validate the users name using the validation tool.
    After that, use the tools to handle the appointments.
    """

    def __init__(self, model: ChatOpenAI):
        """
        Initializes the agent, its tools, and all required components.

        Args:
            model: An instance of a LangChain chat model.
        """

        self.conversation = {'messages': []}

        # Define the list of tools, pointing to the class methods
        tools = [
            self._validation_tool,
            self._new_appointment_tool,
            self._list_appointment_tool,
            self._confirm_appointment_tool,
            self._cancel_appointment_tool
        ]

        # Create and store the final agent
        self.supervisor = create_react_agent(
            model=model, 
            tools=tools, 
            prompt=self._SYSTEM_PROMPT
        )

    def _validation_tool(self, message: str) -> str:
        """
        This tool is used to validate the patients info.
        This tool requires a json format as input
        Required fields:
        - full_name
        - phone_number
        - birth_date (YYYY-MM-DD)

        If the birth_date is not given in the required format, convert it.
        """

        return validate_patient(message)
    
    def _new_appointment_tool(self, message: str) -> str:
        """
        This tool is used to make a new appointment. This tool requires a json format as input
        Required fields:
        - patient_name
        - doctor_name
        - date
        - time

        """
        return new_appointment(message)
    
    def _confirm_appointment_tool(self, message: str) -> str:
        """
        This tool is used to confirm an appointment. This tool requires a json format as input
        Required fields:
        - patient_name
        - doctor_name
        - date
        - time

        """
        return confirm_appointment(message)
    
    def _cancel_appointment_tool(self, message: str) -> str:
        """
        This tool is used to cancel an appointment. This tool requires a json format as input
        Required fields:
        - patient_name
        - doctor_name
        - date
        - time

        """
        return cancel_appointment(message)
    
    def _list_appointment_tool(self, message: str) -> str:
        """
        List all the appointments the patient has.
        Return this to the patient as list and also communicate each corresponding status

        Required fields:
        - patient_name
        """
        return list_appointment(message)

    def invoke(self, message: str) -> dict:
        """
        Runs the agent with a user message.

        Args:
            message: The user's input question.

        Returns:
            The final response from the agent.
        """
        self.conversation['messages'].append(('human', message))
        response = self.supervisor.invoke(self.conversation)
        self.conversation = response
        return response