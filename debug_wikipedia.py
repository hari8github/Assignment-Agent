# First, let's test if Wikipedia is working at all
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
import requests

def test_wikipedia_basic():
    """Test basic Wikipedia functionality"""
    print("🧪 Testing Basic Wikipedia Access...")
    
    try:
        # Test direct Wikipedia API
        api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=500)
        wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)
        
        # Test with a simple, well-known topic
        result = wiki_tool.run("Liverpool Football Club")
        
        print("✅ Wikipedia API is working!")
        print(f"Sample result (first 200 chars): {result[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ Wikipedia API failed: {e}")
        return False

def test_wikipedia_requests():
    """Test if we can access Wikipedia directly"""
    print("\n🧪 Testing Direct Wikipedia Access...")
    
    try:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/Liverpool_F.C."
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Direct Wikipedia access works!")
            print(f"Title: {data.get('title', 'N/A')}")
            print(f"Extract: {data.get('extract', 'N/A')[:100]}...")
            return True
        else:
            print(f"❌ Direct access failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Direct Wikipedia access failed: {e}")
        return False

def test_comprehensive_liverpool_facts():
    """Get comprehensive Liverpool FC facts for verification"""
    print("\n📊 Getting Comprehensive Liverpool FC Facts...")
    
    try:
        api_wrapper = WikipediaAPIWrapper(
            top_k_results=1, 
            doc_content_chars_max=3000,
            load_all_available_meta=True
        )
        wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)
        
        # Get main Liverpool FC page
        main_result = wiki_tool.run("Liverpool Football Club")
        print("📄 Main Liverpool FC Page:")
        print(main_result[:500] + "...")
        
        # Get specific historical info
        history_result = wiki_tool.run("Liverpool F.C. European Cup history")
        print("\n🏆 European Cup History:")
        print(history_result[:500] + "...")
        
        # Get manager info
        managers_result = wiki_tool.run("Liverpool F.C. managers")
        print("\n👨‍💼 Managers Info:")
        print(managers_result[:500] + "...")
        
        return {
            'main': main_result,
            'history': history_result,
            'managers': managers_result
        }
        
    except Exception as e:
        print(f"❌ Comprehensive test failed: {e}")
        return None

def extract_key_facts(wikipedia_data):
    """Extract and verify key Liverpool FC facts"""
    print("\n🔍 Extracting Key Facts...")
    
    if not wikipedia_data:
        print("❌ No Wikipedia data to extract from")
        return
    
    main_text = wikipedia_data['main'].lower()
    
    # Look for founding date
    if '1892' in main_text:
        print("✅ Founded: 1892 (VERIFIED)")
    else:
        print("❌ Founding date not found in Wikipedia")
    
    # Look for European Cup info
    if 'european cup' in main_text or 'champions league' in main_text:
        print("✅ European Cup information found")
        # Extract years if possible
        import re
        years = re.findall(r'19\d{2}|20\d{2}', wikipedia_data['history'])
        if years:
            print(f"📅 Years found in European history: {years[:10]}")
    else:
        print("❌ European Cup information not found")
    
    # Look for key managers
    managers = ['shankly', 'paisley', 'dalglish', 'klopp']
    found_managers = []
    for manager in managers:
        if manager in main_text:
            found_managers.append(manager.title())
    
    if found_managers:
        print(f"✅ Managers found: {', '.join(found_managers)}")
    else:
        print("❌ Key managers not found in main text")

if __name__ == "__main__":
    print("🚀 WIKIPEDIA INTEGRATION DEBUG TEST")
    print("=" * 50)
    
    # Run all tests
    basic_works = test_wikipedia_basic()
    direct_works = test_wikipedia_requests()
    
    if basic_works:
        wikipedia_data = test_comprehensive_liverpool_facts()
        extract_key_facts(wikipedia_data)
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS:")
    
    if basic_works and direct_works:
        print("✅ Wikipedia integration is working")
        print("🔧 Issue is likely in your agent prompt or tool usage")
        print("💡 The agent might not be calling Wikipedia tool properly")
    elif basic_works and not direct_works:
        print("⚠️  Wikipedia API works but direct access blocked")
        print("🔧 Use API wrapper only")
    elif not basic_works:
        print("❌ Wikipedia integration completely broken")
        print("🔧 Need to fix basic Wikipedia access first")
    
    print("\n📋 NEXT STEPS:")
    print("1. If Wikipedia works: Fix agent tool calling")
    print("2. If Wikipedia broken: Install dependencies")
    print("3. Test with simple topics first")
    print("4. Add debug prints to agent execution")