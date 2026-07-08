# services/groq_chat.py
import os
from groq import Groq
from typing import AsyncGenerator, List, Dict

class GroqChatService:
    def __init__(self, quote_context: dict = None):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        self.quote_context = quote_context or {}
    
    async def chat_stream(self, user_message: str, history: List[Dict] = None) -> AsyncGenerator[str, None]:
        """Stream chat responses with quote context"""
        
        system_prompt = self._build_system_prompt()
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        if history:
            messages.extend(history[-10:])
        
        messages.append({"role": "user", "content": user_message})
        
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with quote context"""
        prompt = """You are Domnak AI, a construction cost advisor assistant for Cambodia.

        Your role:
        1. Answer questions about construction costs
        2. Provide negotiation advice
        3. Compare materials and prices
        4. Suggest alternatives or savings opportunities
        
        Be helpful, concise, and use Cambodian context (prices in USD, mention Phnom Penh market where relevant).
        """
        
        if self.quote_context:
            prompt += f"""
            
            CURRENT QUOTE CONTEXT:
            - Total Amount: ${self.quote_context.get('total_amount', 0)}
            - Number of Items: {len(self.quote_context.get('line_items', []))}
            - Contractor: {self.quote_context.get('contractor_name', 'Unknown')}
            
            Key Items in Quote:
            """
            for item in self.quote_context.get('line_items', [])[:5]:
                prompt += f"\n  - {item.get('material_name')}: {item.get('quantity')} {item.get('unit')} @ ${item.get('unit_price')}"
            
            prompt += "\n\nUse this context to answer user questions about this specific quote."
        
        return prompt
