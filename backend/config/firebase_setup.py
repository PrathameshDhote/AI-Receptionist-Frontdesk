"""
Firebase Setup and Initialization Script
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import sys
import argparse

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    backend_dir = Path(__file__).parent.parent
    env_file = backend_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment from: {env_file}\n")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment only\n")


class FirebaseSetup:
    """Firebase setup helper class"""
    
    def __init__(self, credentials_path: str, database_url: str):
        """Initialize Firebase setup."""
        self.credentials_path = credentials_path
        self.database_url = database_url
        self.app = None
        self.success_count = 0
        self.error_count = 0
    
    def verify_credentials(self) -> bool:
        """Verify Firebase credentials file exists and is valid."""
        print("\n" + "="*70)
        print("🔐 STEP 1: Verifying Firebase Credentials")
        print("="*70)
        
        if not os.path.exists(self.credentials_path):
            print(f"❌ Credentials file not found: {self.credentials_path}")
            self.error_count += 1
            return False
        
        print(f"✅ Credentials file found: {self.credentials_path}")
        
        try:
            with open(self.credentials_path, 'r') as f:
                creds_data = json.load(f)
            
            print("✅ Valid JSON format")
            
            required_fields = [
                'type', 'project_id', 'private_key_id', 'private_key',
                'client_email', 'client_id', 'auth_uri', 'token_uri'
            ]
            
            missing_fields = [f for f in required_fields if f not in creds_data]
            
            if missing_fields:
                print(f"❌ Missing fields: {', '.join(missing_fields)}")
                self.error_count += 1
                return False
            
            print(f"✅ All required fields present")
            print(f"\n📌 Credentials Details:")
            print(f"   Project ID: {creds_data.get('project_id')}")
            print(f"   Service Account: {creds_data.get('client_email')}")
            
            self.success_count += 1
            return True
        
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            self.error_count += 1
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            self.error_count += 1
            return False
    
    def initialize_app(self) -> bool:
        """Initialize Firebase Admin SDK."""
        print("\n" + "="*70)
        print("🚀 STEP 2: Initializing Firebase Admin SDK")
        print("="*70)
        
        try:
            cred = credentials.Certificate(self.credentials_path)
            self.app = firebase_admin.initialize_app(cred, {
                'databaseURL': self.database_url
            })
            
            print(f"✅ Firebase initialized successfully")
            print(f"   Database URL: {self.database_url}")
            
            self.success_count += 1
            return True
        
        except ValueError as e:
            if "already exists" in str(e):
                print("   (App already initialized)")
                self.app = firebase_admin.get_app()
                self.success_count += 1
                return True
            print(f"❌ Error: {e}")
            self.error_count += 1
            return False
        
        except Exception as e:
            print(f"❌ Failed: {e}")
            self.error_count += 1
            return False
    
    def create_database_structure(self) -> bool:
        """Create initial database structure."""
        print("\n" + "="*70)
        print("📁 STEP 3: Creating Database Structure")
        print("="*70)
        
        try:
            now = datetime.utcnow().isoformat()
            
            ref = db.reference("/help_requests", app=self.app)
            ref.set({
                "initialized": True,
                "created_at": now,
                "description": "Customer help requests"
            })
            print("✅ Created /help_requests")
            
            ref = db.reference("/knowledge_base", app=self.app)
            ref.set({
                "initialized": True,
                "created_at": now,
                "description": "Salon knowledge base"
            })
            print("✅ Created /knowledge_base")
            
            self.success_count += 1
            return True
        
        except Exception as e:
            print(f"❌ Error: {e}")
            self.error_count += 1
            return False
    
    def add_initial_knowledge_base(self, knowledge_base: Dict[str, str]) -> bool:
        """Add initial knowledge base entries."""
        print("\n" + "="*70)
        print("📚 STEP 4: Adding Initial Knowledge Base")
        print("="*70)
        
        try:
            from uuid import uuid4
            
            ref = db.reference("/knowledge_base", app=self.app)
            
            for i, (question, answer) in enumerate(knowledge_base.items(), 1):
                entry_id = str(uuid4())
                now = datetime.utcnow().isoformat()
                
                entry = {
                    "id": entry_id,
                    "question": question,
                    "answer": answer,
                    "source": "initial",
                    "created_at": now,
                    "updated_at": now,
                    "use_count": 0
                }
                
                ref.child(entry_id).set(entry)
                print(f"   ✓ Entry {i:2d}: {question[:40]}...")
            
            print(f"\n✅ Added {len(knowledge_base)} entries")
            self.success_count += 1
            return True
        
        except Exception as e:
            print(f"❌ Error: {e}")
            self.error_count += 1
            return False
    
    def test_connection(self) -> bool:
        """Test Firebase connection."""
        print("\n" + "="*70)
        print("🧪 STEP 5: Testing Firebase Connection")
        print("="*70)
        
        try:
            ref = db.reference("/", app=self.app)
            data = ref.get()  # FIXED: Removed .val()
            
            if data:
                print(f"✅ Connection successful - Database ready!")
                print(f"\n📊 Database Structure:")
                for key in sorted(data.keys()):
                    value = data[key]
                    if isinstance(value, dict):
                        count = len([k for k in value.keys() if k not in ["initialized", "created_at", "description"]])
                        print(f"   ├─ /{key}: {count} entries")
                    else:
                        print(f"   ├─ /{key}")
                
                print(f"\n✅ Firebase is fully operational!")
            else:
                print(f"✅ Connection successful - Database initialized")
            
            self.success_count += 1
            return True
        
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            print(f"   Debug info: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            self.error_count += 1
            return False
    
    def cleanup(self):
        """Clean up Firebase app"""
        if self.app:
            try:
                firebase_admin.delete_app(self.app)
            except:
                pass
    
    def full_setup(self, knowledge_base: Dict[str, str]) -> bool:
        """Run full setup process."""
        print("\n" + "╔" + "="*68 + "╗")
        print("║" + "🎯 FIREBASE SETUP - Frontdesk AI 🎯".center(70) + "║")
        print("╚" + "="*68 + "╝")
        
        steps = [
            (self.verify_credentials, []),
            (self.initialize_app, []),
            (self.create_database_structure, []),
            (self.add_initial_knowledge_base, [knowledge_base]),
            (self.test_connection, []),
        ]
        
        for step_func, args in steps:
            if not step_func(*args):
                self.cleanup()
                print("\n" + "="*70)
                print(f"❌ Setup failed at: {step_func.__name__}")
                print("="*70)
                return False
        
        self.cleanup()
        
        print("\n" + "="*70)
        print("🎉 FIREBASE SETUP COMPLETE!")
        print("="*70)
        print("\n✅ All 5 steps completed successfully!")
        print(f"   - Credentials verified")
        print(f"   - Firebase connected")
        print(f"   - Database structure created")
        print(f"   - {len(knowledge_base)} knowledge base entries added")
        print(f"   - Connection tested")
        
        print("\n📚 Next Steps:")
        print("   1. Start backend:  uvicorn app.main:app --reload")
        print("   2. Start agent:    python agent/agent.py dev")
        print("   3. Visit API docs: http://localhost:8000/docs")
        print("\n💡 View your data in Firebase Console:")
        print("   https://console.firebase.google.com/project/aireceptionist-80aa4/database")
        
        print("\n" + "="*70 + "\n")
        
        return True


def get_database_url_from_env() -> Optional[str]:
    """Get database URL from environment."""
    db_url = os.getenv("FIREBASE_DATABASE_URL")
    
    if db_url:
        print(f"✅ Using database URL from environment")
        return db_url
    
    print("\n❓ Firebase Database URL not found in environment")
    db_url = input("\n📝 Enter your Firebase Database URL: ").strip()
    
    return db_url if db_url else None


def get_initial_knowledge_base() -> Dict[str, str]:
    """Get initial knowledge base."""
    return {
        "hours": "Monday-Saturday 9 AM to 7 PM, Sunday 10 AM to 5 PM",
        "services": "Hair cutting, coloring, styling, treatments, extensions, perms",
        "prices": "Haircuts from $45, coloring from $85, styling from $35, treatments from $25",
        "location": "123 Beauty Lane, Downtown District, City",
        "phone": "(555) 123-4567",
        "website": "beautyhairsalon.com",
        "booking": "Book online or call (555) 123-4567",
        "parking": "Free parking in building lot",
        "walk_ins": "Walk-ins welcome, appointments recommended",
        "payment_methods": "Cash, credit cards, Apple Pay accepted",
    }


def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="Firebase setup for Frontdesk AI")
    parser.add_argument("--verify", action="store_true", help="Only verify credentials")
    parser.add_argument("--config", default="config/firebase_config.json", help="Credentials path")
    
    args = parser.parse_args()
    
    creds_path = args.config
    db_url = get_database_url_from_env()
    
    if not db_url:
        print("❌ Database URL required")
        sys.exit(1)
    
    setup = FirebaseSetup(creds_path, db_url)
    
    if args.verify:
        success = setup.verify_credentials()
    else:
        knowledge_base = get_initial_knowledge_base()
        success = setup.full_setup(knowledge_base)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
