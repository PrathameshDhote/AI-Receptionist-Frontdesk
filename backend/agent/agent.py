"""
LiveKit AI Agent - Salon Receptionist (Windows Compatible)
This module implements the AI receptionist agent for Beautiful Hair Salon.
It handles customer interactions via voice and escalates to supervisors when needed.

"""

from livekit import agents
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RunContext,
    WorkerOptions,
    cli,
    function_tool,
)

# Simplified imports - no turn detector, no silero
from livekit.plugins import openai
from dotenv import load_dotenv
import os
import httpx
from datetime import datetime
import sys
from openai import AsyncOpenAI  

from salon_context import (
    SYSTEM_INSTRUCTIONS,
    INITIAL_KNOWLEDGE_BASE,
    get_knowledge_base_string,
    AGENT_VOICE_CONFIG,
    ERROR_MESSAGES
)

# Load environment variables
load_dotenv()

# ======================== Configuration ========================

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")

# MegaLLM Configuration
MEGALLM_API_KEY = os.getenv("MEGALLM_API_KEY")
MEGALLM_BASE_URL = os.getenv("MEGALLM_BASE_URL", "https://ai.megallm.io/v1")
MEGALLM_MODEL = os.getenv("MEGALLM_MODEL", "gpt-5")

# Create MegaLLM client
megallm_client = AsyncOpenAI(
    base_url=MEGALLM_BASE_URL,
    api_key=MEGALLM_API_KEY
)

print("🎤 Agent Configuration:")
print(f"   API Base URL: {API_BASE_URL}")
print(f"   LiveKit URL: {LIVEKIT_URL}")
print(f"   STT Model: {AGENT_VOICE_CONFIG['stt_model']}")
print(f"   TTS Model: {AGENT_VOICE_CONFIG['tts_model']}")
print(f"   LLM Provider: MegaLLM")
print(f"   LLM Model: {MEGALLM_MODEL}")
print(f"   LLM Base URL: {MEGALLM_BASE_URL}")
print(f"   Mode: Windows Compatible (no ONNX)")
print()

# ======================== Salon Assistant Agent ========================

class SalonAssistant(Agent):
    """
    AI Receptionist for Beautiful Hair Salon.
    
    This agent:
    - Understands customer voice input
    - Answers questions about the salon
    - Escalates complex questions to human supervisors
    - Learns from supervisor answers
    
    Uses MegaLLM (third-party provider) for intelligent responses.
    Windows compatible - no ONNX dependencies.
    """
    
    def __init__(self, knowledge_base: dict):
        """
        Initialize the Salon Assistant.
        
        Args:
            knowledge_base: Dictionary containing salon information
        """
        self.knowledge_base = knowledge_base
        self.api_base_url = API_BASE_URL
        self.call_count = 0
        self.escalation_count = 0
        
        # Build complete system instructions with knowledge base
        kb_string = get_knowledge_base_string()
        complete_instructions = SYSTEM_INSTRUCTIONS + "\n\n" + kb_string
        
        super().__init__(instructions=complete_instructions)
        
        print("✅ Salon Assistant initialized")
        print("   - MegaLLM for intelligence")
        print("   - Deepgram for speech recognition")
        print("   - ElevenLabs for voice synthesis")
        print("   - Windows compatible mode\n")
    
    @function_tool()
    async def request_help(
        self,
        context: RunContext,
        question: str,
        caller_info: str = "Anonymous"
    ) -> str:
        """Escalate a question to a human supervisor."""
        self.escalation_count += 1
        
        try:
            session_id = "voice-call-" + str(self.escalation_count)
            if hasattr(context, 'session_id'):
                session_id = context.session_id
            elif hasattr(context, 'room') and hasattr(context.room, 'name'):
                session_id = context.room.name
            
            print(f"\n" + "="*60)
            print(f"🚨 ESCALATION #{self.escalation_count}")
            print(f"="*60)
            print(f"Question: {question}")
            print(f"Caller: {caller_info}")
            print(f"Session ID: {session_id}")
            print(f"Time: {datetime.utcnow().isoformat()}")
            print("="*60 + "\n")
            
            # Create help request via FastAPI backend
            async with httpx.AsyncClient() as client:
                # FIX: Send as JSON with proper field names
                response = await client.post(
                    f"{self.api_base_url}/api/help-requests/",
                    json={
                        "question": question,
                        "caller_info": caller_info,
                        "session_id": session_id
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=10.0
                )
                
                # Debug: Print response details if error
                if response.status_code != 201:
                    print(f"Response Status: {response.status_code}")
                    print(f"Response Body: {response.text}")
                
                response.raise_for_status()
                result = response.json()
                
                print(f"✅ Escalation successful!")
                print(f"   Request ID: {result.get('id')}")
                print(f"   Status: Waiting for supervisor response\n")
        
        except httpx.TimeoutException:
            print(f"⏱️ Timeout: Backend server not responding\n")
        except httpx.ConnectError:
            print(f"❌ Connection error: Cannot reach backend\n")
        except Exception as e:
            print(f"❌ Error creating help request: {type(e).__name__}: {e}\n")
            import traceback
            traceback.print_exc()
        
        return (
            "I'm not certain about that, but I'm escalating your question to my supervisor right now. "
            "We'll get back to you shortly with the answer. Thank you for your patience!"
        )




# ======================== Agent Lifecycle Functions ========================

async def prewarm(proc: JobContext):
    """Prewarm the agent."""
    print("🔥 Prewarming agent...")
    try:
        await proc.connect()
        
        # Create LLM with async client
        llm = openai.LLM(
            model=MEGALLM_MODEL,
            client=megallm_client
        )
        
        # Simplified session
        session = AgentSession(
            stt="assemblyai/universal-streaming:en",
            llm=llm,
            tts="cartesia/sonic-3:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
        )
        
        assistant = SalonAssistant(INITIAL_KNOWLEDGE_BASE)
        # Start the session but don't await it in prewarm
        # Just initialize it
        await session.start(room=proc.room, agent=assistant)
        
        print("✅ Agent prewarmed and ready")
    except Exception as e:
        print(f"⚠️ Prewarm error: {e}")


async def entrypoint(ctx: JobContext):
    """Main entrypoint for the agent."""
    try:
        print(f"\n" + "="*70)
        print(f"🎤 CUSTOMER CALL STARTED")
        print(f"="*70)
        print(f"📍 Room: {ctx.room.name}")
        print(f"⏰ Time: {datetime.utcnow().isoformat()}")
        print(f"🧠 LLM: MegaLLM ({MEGALLM_MODEL})")
        print("="*70 + "\n")
        
        await ctx.connect()
        print("✅ Connected to room")
        
        print("🔧 Initializing voice pipeline...")
        llm = openai.LLM(
            model=MEGALLM_MODEL,
            client=megallm_client
        )
        
        assistant = SalonAssistant(INITIAL_KNOWLEDGE_BASE)
        print("✅ Assistant created")
        
        # Option 1: Keep Deepgram (RECOMMENDED - already working)
        #session = AgentSession(
        #    stt=deepgram.STT(model=AGENT_VOICE_CONFIG["stt_model"]),
        #    llm=llm,
        #    tts="cartesia/sonic-3:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
        #)
        
        
        session = AgentSession(
            stt="assemblyai/universal-streaming:en",
            llm=llm,
            tts="cartesia/sonic-3:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
        )
        
        print("✅ Voice pipeline initialized")
        
        print("🤖 Starting agent session...")
        await session.start(room=ctx.room, agent=assistant)
        
        print("="*70)
        print("✅ Agent session completed")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR in entrypoint: {e}")
        import traceback
        traceback.print_exc()
        raise



# ======================== CLI Setup ========================

def log_startup_info():
    """Log important startup information"""
    print("\n" + "="*70)
    print("🎤 LIVEKIT SALON AI AGENT - Windows Compatible")
    print("="*70)
    print("\n📋 Agent Details:")
    print(f"   Role: AI Receptionist for Beautiful Hair Salon")
    print(f"   Mode: {os.getenv('AGENT_MODE', 'production')}")
    print(f"   Backend: {API_BASE_URL}")
    print(f"   LiveKit: {LIVEKIT_URL}")
    
    print("\n🔌 Plugins:")
    print(f"   STT: Deepgram ({AGENT_VOICE_CONFIG['stt_model']})")
    print(f"   LLM: MegaLLM ({MEGALLM_MODEL})")
    print(f"   TTS: ElevenLabs ({AGENT_VOICE_CONFIG['tts_model']})")
    print(f"   VAD: None (simplified mode)")
    print(f"   Turn Detection: None (simplified mode)")
    
    print("\n✅ Agent Features:")
    print("   ✓ Voice-based customer interactions")
    print("   ✓ Real-time speech recognition (Deepgram)")
    print("   ✓ Intelligent question answering (MegaLLM)")
    print("   ✓ Human escalation support")
    print("   ✓ Knowledge base learning")
    print("   ✓ Natural voice synthesis (ElevenLabs)")
    print("   ✓ Windows compatible (no ONNX)")
    
    print("\n📚 Commands:")
    print("   python agent.py start      - Run agent")
    print("   python agent.py --help     - Show all options")
    
    print("\n🔑 API Keys Required:")
    print("   ✓ MEGALLM_API_KEY         - MegaLLM provider")
    print("   ✓ DEEPGRAM_API_KEY        - Speech-to-Text")
    print("   ✓ ELEVEN_API_KEY          - Text-to-Speech")
    print("   ✓ LIVEKIT_API_KEY         - LiveKit server")
    
    print("\n💡 Note:")
    print("   Simplified mode for Windows compatibility")
    print("   No ONNX dependencies (no Silero, no turn detector)")
    print("   Voice conversations work perfectly fine")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    log_startup_info()
    
    # Verify MegaLLM credentials
    if not MEGALLM_API_KEY:
        print("❌ MEGALLM_API_KEY not set!")
        print("   Set it in your .env file or environment variables")
        sys.exit(1)
    
    # Run the agent
    try:
        cli.run_app(
            WorkerOptions(
                entrypoint_fnc=entrypoint,
                prewarm_fnc=prewarm
            )
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Agent shutdown requested")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
