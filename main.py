from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, wiki_tool, save_tool, get_all_sources, search_tracker, wiki_tracker  
import json
import re
from datetime import datetime

load_dotenv()

# Clear previous sources at start
search_tracker.found_sources = []
wiki_tracker.found_sources = []

class AssignmentResponse(BaseModel):
    topic: str
    author: str
    date: str
    introduction: str
    main_sections: list[dict]  # Each dict has 'title' and 'content'
    conclusion: str
    sources: list[str]
    tools_used: list[str]

llm = ChatGroq(model="llama3-8b-8192")

# Enhanced research strategy prompt
research_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are a thorough academic researcher. Your job is to conduct comprehensive Wikipedia research on a topic.
        
        RESEARCH STRATEGY:
        1. Start with the main topic on Wikipedia
        2. Research 4-5 related subtopics or aspects
        3. Look for specific examples, case studies, and real-world applications
        4. Find historical context and recent developments
        5. Research different perspectives and controversies
        
        For the topic "{topic}", research these areas:
        - Main concept and definitions
        - Historical development and key milestones
        - Current applications and examples
        - Different perspectives or schools of thought
        - Recent developments and future trends
        - Specific case studies or notable examples
        
        Use the Wikipedia tool to research each area thoroughly. Take detailed notes.
        """
    ),
    ("human", "Research the topic: {topic}"),
    ("placeholder", "{agent_scratchpad}")
])

# Simplified writing prompt with strict JSON output
writing_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an expert academic writer creating a comprehensive university-level assignment.
        
        CRITICAL: You MUST respond with ONLY a valid JSON object. No other text, no explanations, no markdown formatting.
        
        Based on your Wikipedia research, create a well-structured assignment with:
        - University-level depth and analysis
        - Each section should be 300-400 words
        - Specific examples, dates, names, and case studies from your research
        - Formal academic tone
        - Multiple perspectives and critical analysis
        
        JSON FORMAT - Your response must be EXACTLY this structure with no additional text:
        {{
            "topic": "The exact topic provided",
            "author": "AI Research Assistant", 
            "date": "{current_date}",
            "introduction": "A comprehensive introduction that defines key terms, provides context, and outlines the assignment. Should be 150-200 words based on your Wikipedia research.",
            "main_sections": [
                {{
                    "title": "First Section Title",
                    "content": "Detailed content for this section (300-400 words) with specific examples and analysis based on Wikipedia research."
                }},
                {{
                    "title": "Second Section Title", 
                    "content": "Detailed content for this section (300-400 words) with specific examples and analysis based on Wikipedia research."
                }},
                {{
                    "title": "Third Section Title",
                    "content": "Detailed content for this section (300-400 words) with specific examples and analysis based on Wikipedia research."
                }},
                {{
                    "title": "Fourth Section Title",
                    "content": "Detailed content for this section (300-400 words) with specific examples and analysis based on Wikipedia research."
                }}
            ],
            "conclusion": "A comprehensive conclusion that synthesizes insights, discusses implications, and suggests future directions. Should be 150-200 words.",
            "sources": [],
            "tools_used": ["wikipedia"]
        }}
        
        RESPOND WITH ONLY THE JSON OBJECT. NO OTHER TEXT BEFORE OR AFTER.
        """
    ),
    ("placeholder", "{chat_history}"),
    ("human", "Based on your research, write a comprehensive academic assignment on: {query}"),
    ("placeholder", "{agent_scratchpad}")
])

def create_enhanced_assignment(topic: str):
    """Create assignment using two-stage process: research then write"""
    
    # Stage 1: Research
    print("🔍 Stage 1: Conducting thorough research...")
    research_agent = create_tool_calling_agent(llm=llm, prompt=research_prompt, tools=[wiki_tool])
    research_executor = AgentExecutor(agent=research_agent, tools=[wiki_tool], verbose=True)
    
    # Clear previous sources
    from tools import search_tracker, wiki_tracker
    search_tracker.found_sources = []
    wiki_tracker.found_sources = []
    
    # Conduct research
    research_result = research_executor.invoke({"topic": topic})
    
    # Stage 2: Write assignment
    print("\n✍️  Stage 2: Writing comprehensive assignment...")
    current_date = datetime.now().strftime("%B %d, %Y")
    
    writing_agent = create_tool_calling_agent(
        llm=llm, 
        prompt=writing_prompt.partial(current_date=current_date), 
        tools=[save_tool]
    )
    writing_executor = AgentExecutor(agent=writing_agent, tools=[save_tool], verbose=True)
    
    # Write the assignment
    writing_result = writing_executor.invoke({"query": topic})
    
    # Extract and clean the output
    output = writing_result.get("output", "")
    
    # Clean the JSON output
    cleaned_output = clean_json_output(output)
    
    # Parse and add sources
    try:
        parsed_data = json.loads(cleaned_output)
        
        # Add collected sources if missing or empty
        if not parsed_data.get('sources') or len(parsed_data['sources']) == 0:
            collected_sources = get_all_sources()
            parsed_data['sources'] = collected_sources
        
        # Ensure tools_used is set
        if not parsed_data.get('tools_used'):
            parsed_data['tools_used'] = ["wikipedia"]
        
        # Convert back to JSON string for return
        final_output = json.dumps(parsed_data, indent=2)
        
        return {"output": final_output}
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        # Return error structure
        error_response = {
            "topic": topic,
            "author": "AI Research Assistant",
            "date": current_date,
            "introduction": "Error occurred during assignment generation.",
            "main_sections": [
                {
                    "title": "Error Section",
                    "content": f"An error occurred while generating the assignment: {str(e)}"
                }
            ],
            "conclusion": "Please try again.",
            "sources": get_all_sources(),
            "tools_used": ["wikipedia"]
        }
        return {"output": json.dumps(error_response, indent=2)}

def clean_json_output(output: str) -> str:
    """Clean and extract JSON from agent output"""
    if not output:
        raise ValueError("Empty output received")
    
    # Remove any markdown formatting
    cleaned = output.strip()
    
    # Remove code block markers if present
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[1].split("```")[0].strip()
    elif "```" in cleaned:
        cleaned = cleaned.split("```")[1].split("```")[0].strip()
    
    # Find JSON object using regex
    json_pattern = r'\{.*\}'
    json_match = re.search(json_pattern, cleaned, re.DOTALL)
    
    if json_match:
        return json_match.group()
    else:
        # If no JSON found, assume the entire cleaned output is JSON
        return cleaned

def main():
    """Main execution function"""
    query = input("Enter the topic for the assignment: ")
    print(f"Creating comprehensive assignment on: {query}")
    print("This will involve thorough research and detailed writing...\n")
    
    try:
        # Use two-stage process
        result = create_enhanced_assignment(query)
        
        output = result.get("output")
        
        if not output:
            raise ValueError("No output received from the agent.")
        
        print("Assignment generated successfully!")
        
        # Parse and validate the output
        try:
            parsed_data = json.loads(output)
            structured_response = AssignmentResponse.model_validate(parsed_data)
            
            # Quality assessment
            total_words = len(structured_response.introduction.split())
            for section in structured_response.main_sections:
                total_words += len(section['content'].split())
            total_words += len(structured_response.conclusion.split())
            
            print("\n" + "="*60)
            print("ENHANCED ASSIGNMENT COMPLETED")
            print("="*60)
            print(f"Topic: {structured_response.topic}")
            print(f"Total Word Count: ~{total_words} words")
            print(f"Sections: {len(structured_response.main_sections)}")
            print(f"Sources: {len(structured_response.sources)}")
            print(f"Research Depth: {'High' if total_words > 1500 else 'Medium' if total_words > 1000 else 'Low'}")
            print("="*60)
            
            # Save to file using the save tool
            save_result = save_tool.func(output)
            print(f"\n✅ {save_result}")
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print("Raw output:", output[:500] + "..." if len(output) > 500 else output)
        except Exception as e:
            print(f"❌ Validation error: {e}")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Please try again or check your configuration.")

if __name__ == "__main__":
    main()