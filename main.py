import pandas as pd
import json
from crewai import Agent, Task, Crew, Process
from tools.crew_tools import BookSearchTool, BookAnalyticsTool

# Instantiate the custom tools
book_search_tool = BookSearchTool()
book_analytics_tool = BookAnalyticsTool()

# Define the Book Search Assistant Agent
book_search_agent = Agent(
    role='Book Search Assistant',
    goal='Assist users with their book-related queries. You can either search for specific books or perform analysis on the book data. If the user query is a simple greeting or not book-related, provide a friendly response without using any tools.',
    backstory=(
        'You are Alex, a friendly and knowledgeable AI librarian. You\'re passionate about helping people find their next favorite book. '
        'You chat with users like a real person, avoiding robotic language. When asked about books, you eagerly use your tools to provide insightful recommendations and analysis. '
        'For anything else, you keep the conversation light and steer it back to books.'
    ),
    verbose=True,
    allow_delegation=False,
    tools=[book_search_tool, book_analytics_tool],
)

# Define the search task
search_task = Task(
    description='Analyze the user query: "{query}" and select the appropriate tool to either search for books or perform data analysis. The query could be a search for a specific book or an analytical question about the book data.',
    expected_output='A warm, natural, and helpful response in plain language. Imagine you are talking to a friend.\n'
                  '- For book searches, you might say something like: "I found a few books you might like! Here they are:" and then list them clearly.\n'
                  '- For analysis, you could say: "That\'s a great question! I looked at the data, and it seems that..." and then explain the findings simply.\n'
                  '- Always avoid technical jargon, JSON, or just dumping data. The goal is a delightful conversation.',
    agent=book_search_agent
)

# Assemble the crew
book_search_crew = Crew(
    agents=[book_search_agent],
    tasks=[search_task],
    process=Process.sequential,
    verbose=True,
    # memory=True
)

if __name__ == '__main__':
    queries = [
        "show me the cheapest books in the thriller genre",
        "what are the most popular horror books?", 
        "compare the average price of books between stores",
        "find me some books by Stephen King",
        "find me a book about a stranded astronaut",
        "what is the most popular genre in each bookstore?",
        "which store has better prices for science fiction books?",
        "find highly rated books under $15",
        "compare Andy Weir book prices between stores",
        "show me fantasy books with good reviews"
    ]

    all_results = []

    for query in queries:
        print(f"\n🚀 Kicking off the crew with query: '{query}'")
        result = book_search_crew.kickoff(inputs={'query': query})
        
        # Save the query and the agent's final response.
        all_results.append({'query': query, 'response': result})

        # Clear the last result from the tool to prepare for the next run.
        for tool in book_search_agent.tools:
            if tool.last_result:
                tool.last_result = None
                break

        print("\n✅ Crew execution finished!")
        print("\nFinal Result:")
        print(result)

    # Save all results to a CSV file
    if all_results:
        df = pd.DataFrame(all_results)
        # Reorder columns to have query and title first
        cols = df.columns.tolist()
        if 'query' in cols:
            cols.insert(0, cols.pop(cols.index('query')))
        if 'title' in cols:
            cols.insert(1, cols.pop(cols.index('title')))
        df = df[cols]
        
        df.to_csv('batch_query_results.csv', index=False)
        print("\n✅ Batch processing complete. All results saved to 'batch_query_results.csv'.")
    else:
        print("\n❌ No results to save.")
