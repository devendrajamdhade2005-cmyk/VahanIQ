"""
LLM service for repair guide generation
Supports both Anthropic Claude and OpenAI GPT
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for generating repair guides using LLMs
    Supports Claude (Anthropic) and GPT (OpenAI)
    """
    
    def __init__(self):
        """Initialize LLM service"""
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.client = None
        self._initialized = False
    
    def initialize(self):
        """Initialize the LLM client based on provider"""
        if self._initialized:
            return
        
        try:
            if self.provider == "anthropic":
                from anthropic import AsyncAnthropic
                
                if not settings.ANTHROPIC_API_KEY:
                    raise ValueError("ANTHROPIC_API_KEY not set in environment")
                
                self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
                logger.info(f"Initialized Anthropic client with model: {self.model}")
                
            elif self.provider == "openai":
                from openai import AsyncOpenAI
                
                if not settings.OPENAI_API_KEY:
                    raise ValueError("OPENAI_API_KEY not set in environment")
                
                self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info(f"Initialized OpenAI client with model: {self.model}")
                
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
            
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            raise
    
    async def generate_repair_guide(
        self,
        vehicle_info: Dict[str, Any],
        ml_prediction: Dict[str, Any],
        rag_context: Dict[str, Any],
        diagnosis_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive repair guide
        
        Args:
            vehicle_info: Vehicle details (make, model, year, mileage)
            ml_prediction: ML model prediction with explanation
            rag_context: RAG retrieved context (knowledge + similar cases)
            diagnosis_description: Optional custom diagnosis description
            
        Returns:
            Generated repair guide with steps, parts, cost, time
        """
        self.initialize()
        
        # Build prompt
        prompt = self._build_repair_guide_prompt(
            vehicle_info=vehicle_info,
            ml_prediction=ml_prediction,
            rag_context=rag_context,
            diagnosis_description=diagnosis_description
        )
        
        # Generate with appropriate provider
        if self.provider == "anthropic":
            response = await self._generate_with_claude(prompt)
        elif self.provider == "openai":
            response = await self._generate_with_openai(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
        
        # Parse and structure response
        repair_guide = self._parse_repair_guide(response)
        
        # Add metadata
        repair_guide["metadata"] = {
            "generated_at": datetime.utcnow().isoformat(),
            "llm_provider": self.provider,
            "llm_model": self.model,
            "ml_confidence": ml_prediction.get("probability", 0),
            "rag_articles_used": len(rag_context.get("knowledge_articles", [])),
            "similar_cases_used": len(rag_context.get("similar_cases", []))
        }
        
        return repair_guide
    
    async def generate_diagnosis_summary(
        self,
        vehicle_info: Dict[str, Any],
        sensor_data: Dict[str, Any],
        ml_prediction: Dict[str, Any]
    ) -> str:
        """
        Generate plain-language diagnosis summary for customers
        
        Args:
            vehicle_info: Vehicle details
            sensor_data: Current sensor readings
            ml_prediction: ML prediction results
            
        Returns:
            Customer-friendly diagnosis summary
        """
        self.initialize()
        
        prompt = self._build_diagnosis_summary_prompt(
            vehicle_info=vehicle_info,
            sensor_data=sensor_data,
            ml_prediction=ml_prediction
        )
        
        if self.provider == "anthropic":
            response = await self._generate_with_claude(prompt, max_tokens=500)
        else:
            response = await self._generate_with_openai(prompt, max_tokens=500)
        
        return response.strip()
    
    async def generate_cost_estimate(
        self,
        failure_type: str,
        vehicle_info: Dict[str, Any],
        rag_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate detailed cost estimate based on similar cases and manuals
        
        Args:
            failure_type: Type of failure
            vehicle_info: Vehicle details
            rag_context: RAG context with pricing info
            
        Returns:
            Cost breakdown with parts and labor
        """
        self.initialize()
        
        prompt = self._build_cost_estimate_prompt(
            failure_type=failure_type,
            vehicle_info=vehicle_info,
            rag_context=rag_context
        )
        
        if self.provider == "anthropic":
            response = await self._generate_with_claude(prompt, max_tokens=800)
        else:
            response = await self._generate_with_openai(prompt, max_tokens=800)
        
        # Parse cost estimate
        return self._parse_cost_estimate(response)
    
    def _build_repair_guide_prompt(
        self,
        vehicle_info: Dict[str, Any],
        ml_prediction: Dict[str, Any],
        rag_context: Dict[str, Any],
        diagnosis_description: Optional[str] = None
    ) -> str:
        """Build comprehensive prompt for repair guide generation"""
        
        # Extract key information
        vehicle_str = f"{vehicle_info.get('make', 'Unknown')} {vehicle_info.get('model', 'Unknown')} ({vehicle_info.get('year', 'N/A')})"
        failure_type = ml_prediction.get("failure_type", "unknown")
        probability = ml_prediction.get("probability", 0) * 100
        severity = ml_prediction.get("severity", "unknown")
        ml_explanation = ml_prediction.get("explanation", "")
        
        # Format knowledge articles
        knowledge_str = ""
        for i, article in enumerate(rag_context.get("knowledge_articles", [])[:3], 1):
            knowledge_str += f"\n{i}. {article['title']}\n{article['content'][:800]}...\n"
        
        # Format similar cases
        similar_cases_str = ""
        for i, case in enumerate(rag_context.get("similar_cases", [])[:3], 1):
            similar_cases_str += f"\n{i}. Case #{case.get('repair_case_id')}\n"
            similar_cases_str += f"   Description: {case.get('description', 'N/A')}\n"
            similar_cases_str += f"   Resolution: {case.get('resolution_notes', 'N/A')}\n"
            similar_cases_str += f"   Cost: ₹{case.get('cost', 0):.2f}\n"
            similar_cases_str += f"   Time: {case.get('duration_hours', 0):.1f} hours\n"
        
        prompt = f"""You are an expert automotive technician creating a detailed repair guide for a mechanic.

VEHICLE INFORMATION:
- Vehicle: {vehicle_str}
- Mileage: {vehicle_info.get('mileage', 'Unknown')} km
- Registration: {vehicle_info.get('registration_number', 'N/A')}

AI DIAGNOSIS:
- Failure Type: {failure_type.upper()}
- Confidence: {probability:.1f}%
- Severity: {severity.upper()}
- ML Explanation: {ml_explanation}
{f"- Mechanic's Notes: {diagnosis_description}" if diagnosis_description else ""}

RELEVANT REPAIR MANUALS:
{knowledge_str if knowledge_str else "No relevant manuals found."}

SIMILAR PAST CASES:
{similar_cases_str if similar_cases_str else "No similar cases found."}

TASK:
Generate a comprehensive, step-by-step repair guide for a mechanic. The guide should be practical, detailed, and actionable.

OUTPUT FORMAT (JSON):
{{
  "diagnosis_summary": "Brief summary of the issue in plain language",
  "root_cause": "Most likely root cause based on symptoms and data",
  "urgency": "immediate|urgent|moderate|low",
  "repair_steps": [
    {{
      "step_number": 1,
      "title": "Step title",
      "description": "Detailed step description",
      "safety_warning": "Safety note if applicable",
      "estimated_time_minutes": 15
    }}
  ],
  "required_parts": [
    {{
      "part_name": "Part name",
      "part_number": "Part number if known",
      "quantity": 1,
      "estimated_cost_inr": 2500,
      "priority": "critical|recommended|optional"
    }}
  ],
  "required_tools": ["Tool 1", "Tool 2"],
  "estimated_labor_hours": 2.5,
  "estimated_total_cost_inr": 8500,
  "safety_precautions": ["Safety point 1", "Safety point 2"],
  "quality_checks": ["Check 1", "Check 2"],
  "common_mistakes": ["Mistake to avoid 1", "Mistake to avoid 2"],
  "additional_notes": "Any additional important information"
}}

Generate the repair guide now. Output ONLY valid JSON, no additional text."""
        
        return prompt
    
    def _build_diagnosis_summary_prompt(
        self,
        vehicle_info: Dict[str, Any],
        sensor_data: Dict[str, Any],
        ml_prediction: Dict[str, Any]
    ) -> str:
        """Build prompt for customer-friendly diagnosis summary"""
        
        vehicle_str = f"{vehicle_info.get('make', 'Unknown')} {vehicle_info.get('model', 'Unknown')}"
        failure_type = ml_prediction.get("failure_type", "unknown")
        probability = ml_prediction.get("probability", 0) * 100
        severity = ml_prediction.get("severity", "unknown")
        
        prompt = f"""You are explaining a vehicle diagnosis to a car owner in simple, non-technical language.

Vehicle: {vehicle_str}
Issue Type: {failure_type}
Confidence Level: {probability:.0f}%
Severity: {severity}

AI Analysis: {ml_prediction.get('explanation', '')}

Write a brief, friendly explanation (2-3 sentences) that:
1. Explains what's wrong in simple terms
2. Mentions the severity/urgency
3. Reassures them or advises immediate action as appropriate

Use conversational language. Avoid technical jargon. Be empathetic and helpful."""
        
        return prompt
    
    def _build_cost_estimate_prompt(
        self,
        failure_type: str,
        vehicle_info: Dict[str, Any],
        rag_context: Dict[str, Any]
    ) -> str:
        """Build prompt for cost estimation"""
        
        vehicle_str = f"{vehicle_info.get('make', 'Unknown')} {vehicle_info.get('model', 'Unknown')}"
        
        # Extract pricing from similar cases
        similar_costs = []
        for case in rag_context.get("similar_cases", []):
            if case.get("cost"):
                similar_costs.append({
                    "cost": case["cost"],
                    "duration": case.get("duration_hours", 0)
                })
        
        prompt = f"""Generate a cost estimate for repairing a {failure_type} issue on a {vehicle_str}.

SIMILAR PAST REPAIRS:
{json.dumps(similar_costs, indent=2) if similar_costs else "No historical data available"}

OUTPUT FORMAT (JSON):
{{
  "parts_cost_min": 5000,
  "parts_cost_max": 8000,
  "labor_cost_min": 2000,
  "labor_cost_max": 3500,
  "labor_hours": 2.5,
  "total_cost_min": 7000,
  "total_cost_max": 11500,
  "breakdown": [
    {{"item": "Part 1", "cost": 5000}},
    {{"item": "Labor", "cost": 2500}}
  ],
  "confidence": "high|medium|low",
  "notes": "Additional cost considerations"
}}

Generate cost estimate. Output ONLY valid JSON."""
        
        return prompt
    
    async def _generate_with_claude(
        self,
        prompt: str,
        max_tokens: int = 2000
    ) -> str:
        """Generate text using Claude API"""
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.3,  # Lower temperature for more consistent output
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Claude generation failed: {e}")
            raise
    
    async def _generate_with_openai(
        self,
        prompt: str,
        max_tokens: int = 2000
    ) -> str:
        """Generate text using OpenAI GPT API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.3,
                messages=[{
                    "role": "system",
                    "content": "You are an expert automotive technician providing detailed repair guidance."
                }, {
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise
    
    def _parse_repair_guide(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured repair guide"""
        try:
            # Extract JSON from response (handle markdown code blocks)
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            repair_guide = json.loads(response.strip())
            
            # Validate required fields
            required_fields = [
                "diagnosis_summary", "root_cause", "urgency",
                "repair_steps", "required_parts", "estimated_total_cost_inr"
            ]
            
            for field in required_fields:
                if field not in repair_guide:
                    repair_guide[field] = self._get_default_value(field)
            
            return repair_guide
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse repair guide JSON: {e}")
            logger.error(f"Response was: {response[:500]}")
            
            # Return fallback structure
            return {
                "diagnosis_summary": "Unable to generate structured guide. See raw analysis.",
                "root_cause": "Analysis parsing failed",
                "urgency": "moderate",
                "repair_steps": [{
                    "step_number": 1,
                    "title": "Manual Review Required",
                    "description": response[:500],
                    "estimated_time_minutes": 30
                }],
                "required_parts": [],
                "required_tools": [],
                "estimated_labor_hours": 2.0,
                "estimated_total_cost_inr": 5000,
                "safety_precautions": [],
                "quality_checks": [],
                "common_mistakes": [],
                "additional_notes": "Structured parsing failed. Review raw LLM output."
            }
    
    def _parse_cost_estimate(self, response: str) -> Dict[str, Any]:
        """Parse cost estimate response"""
        try:
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            cost_estimate = json.loads(response.strip())
            return cost_estimate
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse cost estimate: {e}")
            
            # Return fallback
            return {
                "parts_cost_min": 5000,
                "parts_cost_max": 10000,
                "labor_cost_min": 2000,
                "labor_cost_max": 4000,
                "labor_hours": 2.0,
                "total_cost_min": 7000,
                "total_cost_max": 14000,
                "confidence": "low",
                "notes": "Cost estimation failed. These are approximate ranges."
            }
    
    def _get_default_value(self, field: str) -> Any:
        """Get default value for missing field"""
        defaults = {
            "diagnosis_summary": "Diagnosis analysis pending",
            "root_cause": "To be determined",
            "urgency": "moderate",
            "repair_steps": [],
            "required_parts": [],
            "required_tools": [],
            "estimated_labor_hours": 2.0,
            "estimated_total_cost_inr": 5000,
            "safety_precautions": [],
            "quality_checks": [],
            "common_mistakes": [],
            "additional_notes": ""
        }
        return defaults.get(field, None)


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get singleton LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
