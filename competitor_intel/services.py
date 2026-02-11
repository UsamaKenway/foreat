import os
import json
import asyncio
import random
from datetime import date, timedelta
from openai import OpenAI
from .models import Competitor, CompetitorTraffic, CompetitorDeal
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from asgiref.sync import async_to_sync

class CompetitorAgent:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.use_dummy = os.getenv("USE_DUMMY", "True").lower() == "true"
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def analyze_location(self, location_name):
        if self.use_dummy or not self.client:
            return self._analyze_location_dummy(location_name)
        
        return async_to_sync(self._analyze_location_real)(location_name)

    async def _analyze_location_real(self, location_name):
        # 1. Setup MCP Connections
        # Google Maps (SSE)
        gm_url = "http://localhost:3000/mcp"
        
        # Firecrawl (Stdio)
        fc_params = StdioServerParameters(
            command="npx",
            args=["-y", "firecrawl-mcp"],
            env={**os.environ, "FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY", "")}
        )

        results = []
        
        try:
            async with sse_client(gm_url) as (gm_read, gm_write):
                async with ClientSession(gm_read, gm_write) as gm_session:
                    await gm_session.initialize()
                    
                    async with stdio_client(fc_params) as (fc_read, fc_write):
                        async with ClientSession(fc_read, fc_write) as fc_session:
                            await fc_session.initialize()
                            
                            # 2. Get Tools
                            gm_tools = await gm_session.list_tools()
                            fc_tools = await fc_session.list_tools()
                            
                            openai_tools = []
                            tool_map = {} # To keep track of which session owns which tool
                            
                            for tool in gm_tools.tools:
                                openai_tools.append({
                                    "type": "function",
                                    "function": {
                                        "name": f"gm_{tool.name}",
                                        "description": tool.description,
                                        "parameters": tool.inputSchema
                                    }
                                })
                                tool_map[f"gm_{tool.name}"] = (gm_session, tool.name)
                                
                            for tool in fc_tools.tools:
                                openai_tools.append({
                                    "type": "function",
                                    "function": {
                                        "name": f"fc_{tool.name}",
                                        "description": tool.description,
                                        "parameters": tool.inputSchema
                                    }
                                })
                                tool_map[f"fc_{tool.name}"] = (fc_session, tool.name)

                            # 3. Initial Prompt
                            messages = [
                                {"role": "system", "content": f"You are a restaurant market researcher. I am a food restaurant in {location_name}. Find me 3-5 key competitors in my area using Google Maps and search for their current deals using Firecrawl. Gather their name, address, place_id (if available), and cuisine type."},
                                {"role": "user", "content": f"Analyze competitors in {location_name}."}
                            ]

                            # 4. Tool Execution Loop
                            for _ in range(10): # Limit iterations
                                response = self.client.chat.completions.create(
                                    model="gpt-4o",
                                    messages=messages,
                                    tools=openai_tools
                                )
                                
                                response_message = response.choices[0].message
                                messages.append(response_message)
                                
                                if not response_message.tool_calls:
                                    break
                                    
                                for tool_call in response_message.tool_calls:
                                    tool_name = tool_call.function.name
                                    tool_args = json.loads(tool_call.function.arguments)
                                    
                                    if tool_name in tool_map:
                                        session, original_name = tool_map[tool_name]
                                        result = await session.call_tool(original_name, arguments=tool_args)
                                        messages.append({
                                            "role": "tool",
                                            "tool_call_id": tool_call.id,
                                            "name": tool_name,
                                            "content": json.dumps(result.content)
                                        })
                                    else:
                                        messages.append({
                                            "role": "tool",
                                            "tool_call_id": tool_call.id,
                                            "name": tool_name,
                                            "content": "Error: Tool not found"
                                        })

                            # 5. Extract Structured Data
                            struct_prompt = "Based on the gathered information, provide a JSON list of competitors with 'name', 'place_id', 'address', 'cuisine', and 'deals' (a list of strings). Only return the JSON."
                            messages.append({"role": "user", "content": struct_prompt})
                            
                            final_response = self.client.chat.completions.create(
                                model="gpt-4o",
                                messages=messages,
                                response_format={"type": "json_object"}
                            )
                            
                            data = json.loads(final_response.choices[0].message.content)
                            competitors_data = data.get("competitors", []) or data.get("results", [])
                            if not competitors_data and isinstance(data, list):
                                competitors_data = data

                            # 6. Save to Database
                            for comp_data in competitors_data:
                                competitor, created = Competitor.objects.update_or_create(
                                    google_place_id=comp_data.get('place_id') or f"manual_{comp_data['name']}",
                                    defaults={
                                        'name': comp_data['name'],
                                        'location_name': location_name,
                                        'address': comp_data.get('address', ''),
                                        'cuisine_type': comp_data.get('cuisine', 'General')
                                    }
                                )
                                
                                # Traffic Data (Still simulated for now as per requirement "values can be dummy")
                                self._fetch_traffic_data(competitor)
                                
                                # Deals from OpenAI/Firecrawl
                                for deal_text in comp_data.get('deals', []):
                                    CompetitorDeal.objects.update_or_create(
                                        competitor=competitor,
                                        date_observed=date.today(),
                                        deal_title=deal_text,
                                        defaults={
                                            'deal_source_url': 'https://firecrawl.dev/scraped',
                                            'impact_on_traffic': random.uniform(0.05, 0.25)
                                        }
                                    )
                                results.append(competitor)

        except Exception as e:
            print(f"Error in analyze_location_real: {e}")
            # Fallback to dummy if real fails? Or just return empty results
            return self._analyze_location_dummy(location_name)
            
        return results

    def _analyze_location_dummy(self, location_name):
        competitors_data = [
            {'name': f'Green Bistro {location_name}', 'place_id': f'place_{location_name}_1', 'address': f'123 Teal St, {location_name}', 'cuisine': 'Healthy'},
            {'name': f'Urban Eats {location_name}', 'place_id': f'place_{location_name}_2', 'address': f'456 Mint Ave, {location_name}', 'cuisine': 'Fusion'},
            {'name': f'The Healthy Hub {location_name}', 'place_id': f'place_{location_name}_3', 'address': f'789 Sage Rd, {location_name}', 'cuisine': 'Vegan'}
        ]
        
        results = []
        for comp_data in competitors_data:
            competitor, created = Competitor.objects.update_or_create(
                google_place_id=comp_data['place_id'],
                defaults={
                    'name': comp_data['name'],
                    'location_name': location_name,
                    'address': comp_data['address'],
                    'cuisine_type': comp_data['cuisine']
                }
            )
            self._fetch_traffic_data(competitor)
            self._fetch_deals_dummy(competitor)
            results.append(competitor)
        return results

    def _fetch_traffic_data(self, competitor):
        for i in range(14):
            d = date.today() - timedelta(days=i)
            CompetitorTraffic.objects.update_or_create(
                competitor=competitor,
                date=d,
                defaults={
                    'estimated_visits': random.randint(50, 200),
                    'traffic_score': random.randint(30, 95)
                }
            )

    def _fetch_deals_dummy(self, competitor):
        deals = ["Happy Hour 50% Off Drinks", "Buy One Get One Pizza", "Lunch Special: $12", "No active deals"]
        deal_title = random.choice(deals)
        if deal_title != "No active deals":
            CompetitorDeal.objects.update_or_create(
                competitor=competitor,
                date_observed=date.today(),
                deal_title=deal_title,
                defaults={
                    'deal_source_url': 'https://example.com/deals',
                    'impact_on_traffic': random.uniform(0.05, 0.25)
                }
            )
