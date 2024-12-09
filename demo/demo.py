from langchain_openai import ChatOpenAI
import json
from langchain_core.tools import tool
import logging

from typing import Optional, Dict, Any, Tuple
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
import asyncio
from langgraph.prebuilt import create_react_agent
from prompts import extract_twitter_username_prompt, mock_system_message,extract_params_prompt, picture_prompt, SYSTEM_MESSAGES, DEFAULT_SYSTEM_MESSAGE
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, FunctionMessage, ToolMessage
from pydantic import BaseModel, Field
from langchain.chains import LLMChain
import re
from dotenv import load_dotenv
load_dotenv()
import os 
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('demo.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)
llm = ChatOpenAI(
    model = 'gpt-4o',
    api_key=os.getenv('OPENAI_API_KEY'),
)

from langchain_core.tools import tool
def extract_params(text: str):
    """
    Extracts the width, height, and batch_size from the user's input. 
    You need to learn how to extract information from user text input that can be used as a prompt. This prompt information is then passed to the AI for image generation.

    Args:
        text (str): The user input text, which contains useful information which can be used for image generation as a prompt.

    Returns:
        tuple: (prompt, width, height, batch_size), where batch_size defaults to None if unspecified.
    """
    try:
        # Step 1: Attempt regex extraction for width and height
        prompt, width, height, batch_size = None, None, None, None

        # Match dimensions like "1024*512"
        match = re.search(r'(\d+)\s*[xX*]\s*(\d+)', text)
        if match:
            width = int(match.group(1))
            height = int(match.group(2))

        # Match batch size like "3 images"
        batch_match = re.search(r'(\d+)\s*images', text, re.IGNORECASE)
        if batch_match:
            batch_size = int(batch_match.group(1))

        # Step 2: Use the model to extract dimensions if regex fails
        if width is None or height is None or batch_size is None:
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", extract_params_prompt),
                ("human", "{text}")
            ])
            chain = prompt_template | llm | StrOutputParser()

            # chain = LLMChain(llm=llm, 
            #                  prompt=prompt_template, 
            #                 #  verbose=True, 
            #                  output_parser=StrOutputParser()
            # )

            response = chain.invoke(input={"text": text})
            logger.info(f"Response_before: {response}")
            if isinstance(response, (HumanMessage, AIMessage)):
                response = response.content
            elif isinstance(response, dict) and 'text' in response:
                response = response['text']
            logger.info(f"\n\nResponse_final: {response}")

            match = re.search(
                r'prompt:\s*(.*?)(?=,\s*width:),\s*width:\s*(\d+|None),\s*height:\s*(\d+|None),\s*batch_size:\s*(\d+|None)',
                response,
                re.DOTALL
            )
            if match:
                prompt = match.group(1).strip()
                width_str = match.group(2)
                height_str = match.group(3)
                batch_size_str = match.group(4)

                
                width = int(width_str) if width_str != 'None' else None
                height = int(height_str) if height_str != 'None' else None
                batch_size = int(batch_size_str) if batch_size_str != 'None' else None
            else:
                
                match = re.search(
                    r'prompt:\s*(.*?)(?:,\s*width:|$)(.*?)(?:,\s*height:|$)(.*?)(?:,\s*batch_size:|$)(.*?)$',
                    response,
                    re.DOTALL
                )
                if match:
                    prompt = match.group(1).strip()
                   

            logger.info(f"Extracted from model: {prompt}, {width}, {height}, {batch_size}")
            # If prompt wasn't extracted, use the entire input as the prompt

        # print(f"Extracted params - Prompt: {prompt}, Width: {width}, Height: {height}, Batch size: {batch_size}")
        return prompt, width, height, batch_size
     
    except Exception as e:
        logger.error(f"Error in extract_params: {str(e)}")
        # 如果提取参数失败，返回prompt is None, 由 process_image_params 修改给用户的response
        return None, None, None, None


workflow_relation = {
    'text2image': '66f116eb2b2a4e22c8a3cb9a', 
    'image2text': '66f7a3f85a5b0b8e33d3738c'
}

@tool(return_direct=True)
def text_to_image(user_input: str):
    """Generate a picture based on the given user_input.
    This is useful when you need to generate an image based on a user_input.
    Args:
        user_input (str): The user input, which contains useful information which can be used for image generation.
    Returns:
        JSON string containing the workflow_id and the user_input.

    """

    conversation_prompt = ChatPromptTemplate.from_messages([
        ("system", picture_prompt),
        ("human", "{input}")
    ])

    conversation_chain = conversation_prompt | llm | StrOutputParser()
    # conversation_chain = LLMChain(
    #     llm=llm,
    #     prompt=conversation_prompt,
    #     # verbose=True,
    #     output_parser=StrOutputParser()
    # )

    response = conversation_chain.invoke({"input": user_input})
    if isinstance(response, (HumanMessage, AIMessage)):
        response = response.content
    elif isinstance(response, dict) and 'text' in response:
        response = response['text']

    prompt, width, height, batch_size = extract_params(user_input)
    
    logger.info(f"Extracted params - Prompt: {prompt}, Width: {width}, Height: {height}, Batch size: {batch_size}")
    
    if batch_size and batch_size > 4:
        response += "\n\nNote: The requested number of images exceeded the maximum."
        batch_size = 4
        logger.info(f"Batch size adjusted to maximum: {batch_size}")

    if width and height:
        if (width > 1920 or height > 1920) and (width % 16 == 0 and height % 9 == 0 or width % 9 == 0 and height % 16 == 0):
            response += "\n\nThe picture quality is too high! The parameters have been adjusted for you in the right sidebar."
            width = None
            height = None
            logger.info("Image dimensions reset due to high quality")
        elif width > 1920 or height > 1920 or (width % 16 != 0 and height % 9 != 0 and width % 9 != 0 and height % 16 != 0):
            response += "\n\nThe picture quality is too high! The parameters have been proportionally adjusted for you."
            original_width, original_height = width, height
            # The proportion is reduced to 1920 and below
            if width > height:
                height = 1920 * height // width
                width = 1920
            else:
                width = 1920 * width // height
                height = 1920
            logger.info(f"Image dimensions adjusted from {original_width}x{original_height} to {width}x{height}")

    logger.info(f"Final params - Prompt: {prompt}, Width: {width}, Height: {height}, Batch size: {batch_size}")

    if prompt is None:
        response = "I apologize, but I'm having trouble understanding your request at the moment. This might be due to system load or network issues. Please try again in a moment. If the problem persists, you can try rephrasing what kind of image you'd like to create."
        logger.warning("Failed to extract prompt from user input and conversation history")
        return {
            "workflow_id": None,
            "message": response,
            "params": {
                "text": None,
                "width": None,
                "height": None,
                "batch_size": None
            }
        }

    if not workflow_relation:
        logger.error("workflow_id not found.")
        return json.dumps({"error": "workflow_id not found."})
    
    workflow_id = workflow_relation.get('text2image')
    
    if not workflow_id:
        logger.error("Workflow not found.")
        return json.dumps({"error": "Workflow not found."})
    
    result = {
            "workflow_id": workflow_id,
            "message": response,
            "params": {
                "text": prompt,
                "width": width,
                "height": height,
                "batch_size": batch_size
            }
    }
    return json.dumps(result)







# # 定义输出格式的 schema
# class AgentResponse(BaseModel):
#     """Schema for unified agent response format"""
#     workflow_id: Optional[str] = Field(default=None, description="Workflow ID if applicable")
#     message: str = Field(description="Agent's response message")
#     params: Dict[str, Any] = Field(
#         default_factory=lambda: {
#             "text": None,
#             "width": None, 
#             "height": None,
#             "batch_size": None
#         },
#         description="Additional parameters"
#     )


tools = [ text_to_image]
from langgraph.checkpoint.memory import MemorySaver  # an in-memory checkpointer
memory = MemorySaver()

def load_system_message(system_type=None):
    """Reload system message from prompts.py for each conversation
    
    Args:
        system_type (str, optional): Type of system message to load. Defaults to None.
    
    Returns:
        str: The loaded system message
    """
    try:
        # Force reload the module
        import importlib
        import prompts
        importlib.reload(prompts)
        
        if system_type:
            system_message = prompts.SYSTEM_MESSAGES.get(system_type.lower())
            if system_message:
                logger.info(f"Loaded {system_type} system message")
                return system_message
            else:
                logger.warning(f"System message type '{system_type}' not found, using default")
        
        return prompts.DEFAULT_SYSTEM_MESSAGE
    except Exception as e:
        logger.error(f"Error loading system message: {str(e)}")
        return prompts.DEFAULT_SYSTEM_MESSAGE

def create_agent(system_type=None):
    """Create a new agent with fresh system message
    
    Args:
        system_type (str, optional): Type of system message to use. Defaults to None.
    
    Returns:
        Agent: The created agent
    """
    system_message = load_system_message(system_type)
    logger.info(f"Current system message: {system_message}")
    return create_react_agent(
        llm,
        tools,
        state_modifier=system_message,
        checkpointer=memory
    )

def process_agent_response(response):
    """Process agent response into structured format.
    If workflow_id exists, return the ToolMessage content,
    otherwise return the last AIMessage content.
    """
    try:
        logger.info("Starting to process agent response")
        logger.debug(f"Full response messages: {response['messages']}")
        
        # Get the last sequence of messages after the last user input
        messages = response['messages']
        last_human_index = len(messages) - 1
        for i in range(len(messages)-1, -1, -1):
            if isinstance(messages[i], HumanMessage):
                last_human_index = i
                break
                
        relevant_messages = messages[last_human_index:]
        logger.info(f"Processing relevant messages after last human input: {relevant_messages}")
        
        # Find the last ToolMessage in the relevant messages
        tool_message = next((msg for msg in reversed(relevant_messages) 
                           if isinstance(msg, ToolMessage)), None)
        
        logger.info(f"Found tool message: {tool_message is not None}")
        if tool_message:    

            tool_content = json.loads(tool_message.content)
            workflow_id = tool_content.get('workflow_id')
            if workflow_id:
                logger.info(f"Processing tool message content: {tool_message.content}")
                return tool_content    

        logger.info("No valid workflow_id found, using AI message")
        # Get the last AI message from relevant messages
        final_ai_message = next((msg for msg in reversed(relevant_messages) 
                               if isinstance(msg, AIMessage)), None)
        
        if not final_ai_message:
            raise ValueError("No AI message found in response")
            
        logger.info(f"Final AI message content: {final_ai_message.content}")
        
        result = {
            "workflow_id": None,
            "message": final_ai_message.content,
            "params": {
                "text": None,
                "width": None,
                "height": None,
                "batch_size": None
            }
        }
        return result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Error processing agent response: {str(e)}")
        logger.exception("Full exception details:")  # 这会打完整的堆栈跟踪
        return json.dumps({
            "workflow_id": None,
            "message": f"Error processing response: {str(e)}",
            "params": {
                "text": None,
                "width": None,
                "height": None,
                "batch_size": None
            }
        })
    finally:
        logger.info("Finished processing agent response")

# Add config definition
config = {"configurable": {"thread_id": "123"}}

def demo_main():
    print("""
You can modify the prompts in prompts.py and see changes in real-time.
Available system message types:
- mock (default): Horoscope teller
- praise: Professional praiser
- dating: Dating strategist
- roast: Roast master
- fate: Fate reader
- almighty: AI image generation bot
- dream: Dream interpreter
- wellness: Health analyst
- neko: Neko maid
- poetry: Poetry muse

To change system message type, type: /system <type>, e.g. /system praise
Press Ctrl+C to exit.
""")
    
    current_system = None
    
    while True:
        try:
            # Get user input
            query = input("\nUser: ").strip()
            
            # Check if user wants to change system message
            if query.startswith('/system'):
                parts = query.split(maxsplit=1)
                if len(parts) > 1:
                    current_system = parts[1].strip()
                    print(f"System message changed to: {current_system}")
                    continue
                else:
                    print("Please specify a system message type")
                    continue
            
            try:
                # Create new agent for each conversation turn with current system type
                current_agent = create_agent(current_system)
                
                # Pass config to agent invocation
                response = current_agent.invoke(
                    {'messages': [HumanMessage(content=query)]}, 
                    config=config
                )
                logger.info(f"Agent response: {response}")
                
                structured_response = process_agent_response(response)
                logger.info(f"Structured Response: {structured_response}")
                
                if isinstance(structured_response, str):
                    parsed_response = json.loads(structured_response)
                else:
                    parsed_response = structured_response
                
                print(f"Agent: {parsed_response.get('message', 'No response message available')}")
                    
            except Exception as e:
                logger.error(f"Error during agent invocation: {str(e)}")
                print(f"Error: {str(e)}")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            break

if __name__ == "__main__":
    demo_main()