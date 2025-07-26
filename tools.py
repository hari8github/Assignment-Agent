from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper, DuckDuckGoSearchAPIWrapper
from langchain.tools import Tool
from datetime import datetime
import json
import requests
from urllib.parse import urlparse
import re

# Global source collectors
WIKIPEDIA_SOURCES = []
SEARCH_SOURCES = []
RESEARCH_FACTS = {}

class Tracker:
    def __init__(self):
        self.found_sources = []

search_tracker = Tracker()
wiki_tracker = Tracker()

def verify_url(url: str) -> bool:
    """Verify if a URL is accessible and returns 200 status"""
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def forced_wikipedia_research(query: str) -> str:
    """Force comprehensive Wikipedia research and fact collection"""
    global WIKIPEDIA_SOURCES, RESEARCH_FACTS
    
    print(f"🔍 FORCED Wikipedia research for: {query}")
    
    try:
        # Create Wikipedia tool with larger content limit
        api_wrapper = WikipediaAPIWrapper(
            top_k_results=2, 
            doc_content_chars_max=4000,
            load_all_available_meta=True
        )
        wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)
        
        # Get main result
        result = wiki_tool.run(query)
        
        if result and len(result) > 100:  # Ensure we got substantial content
            # Create proper Wikipedia URL
            clean_query = query.replace(' ', '_').replace(',', '').replace(':', '')
            wiki_url = f"https://en.wikipedia.org/wiki/{clean_query}"
            
            # Add to sources if not already present
            source_entry = f"Wikipedia: {query} - {wiki_url}"
            if source_entry not in WIKIPEDIA_SOURCES:
                WIKIPEDIA_SOURCES.append(source_entry)
            
            # Store facts for this query
            RESEARCH_FACTS[query] = {
                'content': result,
                'source': wiki_url,
                'length': len(result)
            }
            
            print(f"✅ Wikipedia research successful for '{query}' - {len(result)} characters")
            return f"WIKIPEDIA RESEARCH ON '{query.upper()}':\n\n{result}\n\n[VERIFIED SOURCE: {wiki_url}]"
            
        else:
            print(f"⚠️  Wikipedia returned minimal content for '{query}'")
            return f"Limited Wikipedia information found for '{query}'. Please try a more specific search term."
            
    except Exception as e:
        print(f"❌ Wikipedia research failed for '{query}': {e}")
        return f"Wikipedia research failed for '{query}': {str(e)}"

def comprehensive_topic_research(main_topic: str) -> str:
    """Research a topic comprehensively with multiple related searches"""
    global RESEARCH_FACTS
    
    print(f"🎯 COMPREHENSIVE research starting for: {main_topic}")
    
    # Define related search terms based on the main topic
    if "liverpool" in main_topic.lower():
        search_terms = [
            "Liverpool Football Club",
            "Liverpool F.C. history", 
            "Liverpool F.C. European Cup",
            "Liverpool F.C. managers",
            "Anfield stadium"
        ]
    elif "ai" in main_topic.lower() or "artificial intelligence" in main_topic.lower():
        search_terms = [
            "Artificial intelligence",
            "Machine learning",
            "AI ethics",
            "AI bias",
            "AI automation"
        ]
    else:
        # Generic approach - search main topic + related terms
        search_terms = [
            main_topic,
            f"{main_topic} history",
            f"{main_topic} examples",
            f"{main_topic} current trends"
        ]
    
    all_research = []
    
    for term in search_terms:
        research = forced_wikipedia_research(term)
        all_research.append(f"### Research on '{term}':\n{research}\n")
        
        # Small delay to be respectful to Wikipedia
        import time
        time.sleep(0.5)
    
    comprehensive_result = "\n".join(all_research)
    
    print(f"📊 COMPREHENSIVE RESEARCH COMPLETE:")
    print(f"   - Terms researched: {len(search_terms)}")
    print(f"   - Total content length: {len(comprehensive_result)}")
    print(f"   - Sources collected: {len(WIKIPEDIA_SOURCES)}")
    
    return comprehensive_result

def save_to_txt_with_real_sources(data: str, filename: str = "assignment.txt"):
    """Save with real Wikipedia sources that were actually researched"""
    global WIKIPEDIA_SOURCES, RESEARCH_FACTS
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        assignment_data = json.loads(data)
        
        # Override sources with actually collected Wikipedia sources
        assignment_data['sources'] = WIKIPEDIA_SOURCES.copy()
        
        # Format as academic assignment
        formatted_text = f"# {assignment_data['topic']}\n\n"
        formatted_text += f"Written by: {assignment_data['author']}\n\n"
        formatted_text += f"Date: {assignment_data['date']}\n\n"
        
        # Introduction
        formatted_text += f"{assignment_data['introduction']}\n\n"
        
        # Main sections
        for i, section in enumerate(assignment_data['main_sections'], 1):
            formatted_text += f"## {i}. {section['title']}\n\n"
            formatted_text += f"{section['content']}\n\n"
        
        # Conclusion
        formatted_text += f"## Conclusion\n\n"
        formatted_text += f"{assignment_data['conclusion']}\n\n"
        
        # Real sources section
        if WIKIPEDIA_SOURCES:
            formatted_text += f"## Sources\n\n"
            for i, source in enumerate(WIKIPEDIA_SOURCES, 1):
                formatted_text += f"{i}. {source}\n"
            formatted_text += "\n"
        else:
            formatted_text += f"## Sources\n\n"
            formatted_text += "⚠️  No Wikipedia sources were successfully captured during research.\n"
            formatted_text += "This indicates a problem with the research process.\n\n"
        
        # Research methodology with statistics
        formatted_text += f"## Research Methodology\n\n"
        formatted_text += f"Tools Used: {', '.join(assignment_data.get('tools_used', ['wikipedia']))}\n"
        formatted_text += f"Wikipedia Articles Researched: {len(RESEARCH_FACTS)}\n"
        formatted_text += f"Total Research Content: {sum(facts['length'] for facts in RESEARCH_FACTS.values())} characters\n"
        formatted_text += f"Generated: {timestamp}\n\n"
        
        # Fact verification section
        if RESEARCH_FACTS:
            formatted_text += f"## Research Sources Detail\n\n"
            for topic, facts in RESEARCH_FACTS.items():
                formatted_text += f"**{topic}**: {facts['length']} characters from {facts['source']}\n"
            formatted_text += "\n"
        
        # Disclaimer
        formatted_text += f"## Disclaimer\n\n"
        formatted_text += "This assignment was generated using AI tools with Wikipedia research. "
        if WIKIPEDIA_SOURCES:
            formatted_text += "All facts should be verified against the listed Wikipedia sources. "
        else:
            formatted_text += "⚠️  NO WIKIPEDIA SOURCES WERE CAPTURED - facts may be unreliable. "
        formatted_text += "Please verify all information and add additional academic sources before submission.\n"
        
    except json.JSONDecodeError as e:
        formatted_text = f"--- Assignment Output ---\nTimestamp: {timestamp}\n\n"
        formatted_text += f"Error formatting data: {e}\nOriginal Data:\n{data}\n"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(formatted_text)
    
    return f"Academic assignment saved to {filename} with {len(WIKIPEDIA_SOURCES)} Wikipedia sources"

def clear_research_cache():
    """Clear all collected research for a fresh start"""
    global WIKIPEDIA_SOURCES, SEARCH_SOURCES, RESEARCH_FACTS
    WIKIPEDIA_SOURCES = []
    SEARCH_SOURCES = []
    RESEARCH_FACTS = {}
    print("🧹 Research cache cleared")

def get_research_summary():
    """Get summary of collected research"""
    global WIKIPEDIA_SOURCES, RESEARCH_FACTS
    
    return {
        'sources_count': len(WIKIPEDIA_SOURCES),
        'research_topics': list(RESEARCH_FACTS.keys()),
        'total_content_length': sum(facts['length'] for facts in RESEARCH_FACTS.values()),
        'sources_list': WIKIPEDIA_SOURCES.copy()
    }

# Create the tools
comprehensive_research_tool = Tool(
    name="comprehensive_wikipedia_research",
    func=comprehensive_topic_research,
    description="Conduct comprehensive Wikipedia research on a topic, including related subtopics. Use this for thorough fact-gathering. Input should be the main topic to research."
)

wikipedia_research_tool = Tool(
    name="wikipedia_research",
    func=forced_wikipedia_research,
    description="Research a specific topic on Wikipedia and collect factual information. Input should be a specific topic or concept to research."
)

save_tool_enhanced = Tool(
    name="save_text_to_file",
    func=save_to_txt_with_real_sources,
    description="Save the assignment with all collected Wikipedia sources and research statistics."
)

# Keep these for compatibility
search_tool = Tool(
    name="search",
    func=lambda x: "Search temporarily disabled - using Wikipedia research only",
    description="Web search tool (currently disabled to focus on Wikipedia research)"
)

wiki_tool = wikipedia_research_tool
save_tool = save_tool_enhanced

# Function to get all collected sources
def get_all_sources():
    """Get all sources collected during research"""
    return WIKIPEDIA_SOURCES.copy()