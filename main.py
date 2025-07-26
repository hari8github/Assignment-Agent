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

# Main writing prompt - much more detailed and specific
writing_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are an expert academic writer creating a comprehensive university-level assignment.
            
            WRITING STANDARDS:
            - University-level depth and analysis (not high school level)
            - Each section should be 400-500 words minimum
            - Use specific examples, dates, names, and case studies
            - Include multiple perspectives and critical analysis
            - Write in formal academic tone with sophisticated vocabulary
            - Avoid cliché phrases like "only as good as the data"
            
            CONTENT REQUIREMENTS:
            - Introduction: Define key terms, provide context, outline what you'll cover (150-200 words)
            - Each main section should include:
              * Clear definition and explanation of the concept
              * Historical context or development
              * 2-3 specific real-world examples with details
              * Different perspectives or viewpoints
              * Current research or developments
              * Critical analysis of implications
            - Conclusion: Synthesize key insights, discuss implications, suggest future directions (150-200 words)
            
            RESEARCH-BASED WRITING:
            - Base your content on the Wikipedia research you conducted
            - Reference specific Wikipedia articles you used
            - Include dates, names, organizations, and specific events
            - Show depth of understanding, not surface-level knowledge
            
            ACADEMIC QUALITY CHECKLIST:
            ✓ Uses specific examples with details (names, dates, companies)
            ✓ Shows understanding of complexity and nuance
            ✓ Includes multiple perspectives
            ✓ Demonstrates critical thinking
            ✓ Uses sophisticated academic vocabulary
            ✓ Avoids oversimplification
            ✓ Connects concepts to broader implications
            
            JSON FORMAT - Your response must be ONLY this JSON structure:
            {{
                "topic": "The exact topic provided",
                "author": "AI Research Assistant",
                "date": "{current_date}",
                "introduction": "A sophisticated introduction that defines key terms, provides historical context, and outlines the assignment scope. Should demonstrate deep understanding and set up complex analysis. (150-200 words)",
                "main_sections": [
                    {{
                        "title": "Descriptive Section Title (not generic)",
                        "content": "A comprehensive section of 400-500 words that includes: clear explanations, historical context, 2-3 specific examples with details (names, dates, organizations), different perspectives, current developments, and critical analysis. Write in paragraph form with academic sophistication."
                    }},
                    {{
                        "title": "Another Specific Section Title",
                        "content": "Another detailed 400-500 word section following the same standards..."
                    }}
                    // Include exactly 4 main sections
                ],
                "conclusion": "A sophisticated conclusion that synthesizes insights, discusses broader implications, acknowledges limitations, and suggests future research directions. Should demonstrate critical thinking and academic maturity. (150-200 words)",
                "sources": ["List Wikipedia articles you actually referenced"],
                "tools_used": ["wikipedia", "search"]
            }}
            
            CRITICAL: Base everything on your Wikipedia research. Be specific, detailed, and academic.
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "Based on your research, write a comprehensive academic assignment on: {query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# Two-stage process: Research then Write
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
    
    return writing_result

# Enhanced main execution
def main():
    query = input("Enter the topic for the assignment: ")
    print(f"Creating comprehensive assignment on: {query}")
    print("This will involve thorough research and detailed writing...\n")
    
    try:
        # Use two-stage process
        raw_response = create_enhanced_assignment(query)
        
        output = raw_response.get("output")
        
        if not output:
            raise ValueError("No output received from the agent.")
        
        print("Assignment generated successfully!")
        
        # Clean and parse JSON
        cleaned_output = output.strip()
        
        if "```json" in cleaned_output:
            cleaned_output = cleaned_output.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned_output:
            cleaned_output = cleaned_output.split("```")[1].split("```")[0].strip()
        
        json_pattern = r'\{.*\}'
        json_match = re.search(json_pattern, cleaned_output, re.DOTALL)
        
        if json_match:
            json_str = json_match.group()
        else:
            json_str = cleaned_output
        
        # Parse and validate
        parsed_data = json.loads(json_str)
        
        # Add collected sources if missing
        if not parsed_data.get('sources') or len(parsed_data['sources']) == 0:
            collected_sources = get_all_sources()
            parsed_data['sources'] = collected_sources
        
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
        
        # Save to file
        save_result = save_tool.func(json_str)
        print(f"\n✅ {save_result}")
        
        # Quality warnings
        if total_words < 1200:
            print("\n⚠️  Note: Assignment may be shorter than typical university standards.")
            print("   Consider requesting more detailed sections.")
            
        if len(structured_response.sources) == 0:
            print("\n⚠️  Warning: No Wikipedia sources were captured during research.")
            print("   Please verify the Wikipedia tool is working correctly.")
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print("The agent may not be returning proper JSON format.")
    except ValueError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Please try again or check your configuration.")

if __name__ == "__main__":
    main()