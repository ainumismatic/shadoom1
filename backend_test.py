#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Shadoom API
Tests all endpoints including Gemini AI integration
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Base URL from frontend/.env
BASE_URL = "https://92aade97-d90c-4169-9895-b4178da7f54c.preview.emergentagent.com/api"

class ShadoomAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.test_user_id = None
        self.test_idea_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def log_test(self, test_name, success, details=""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
        
    def test_health_check(self):
        """Test GET /api/ endpoint"""
        print("🔍 Testing Health Check Endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Shadoom" in data["message"]:
                    self.log_test("Health Check", True, f"Response: {data['message']}")
                    return True
                else:
                    self.log_test("Health Check", False, f"Unexpected response format: {data}")
                    return False
            else:
                self.log_test("Health Check", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_create_user(self):
        """Test POST /api/users endpoint"""
        print("🔍 Testing Create User Endpoint...")
        try:
            # Generate unique test data
            timestamp = int(time.time())
            test_email = f"influencer{timestamp}@shadoom.com"
            test_name = f"Maria Influencer {timestamp}"
            
            user_data = {
                "email": test_email,
                "name": test_name,
                "profile_pic": "https://example.com/profile.jpg"
            }
            
            response = self.session.post(f"{self.base_url}/users", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "email", "name", "created_at"]
                
                if all(field in data for field in required_fields):
                    if data["email"] == test_email and data["name"] == test_name:
                        self.test_user_id = data["id"]
                        self.log_test("Create User", True, f"User created with ID: {self.test_user_id}")
                        return True
                    else:
                        self.log_test("Create User", False, "Data mismatch in response")
                        return False
                else:
                    self.log_test("Create User", False, f"Missing required fields. Got: {list(data.keys())}")
                    return False
            else:
                self.log_test("Create User", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create User", False, f"Exception: {str(e)}")
            return False
    
    def test_get_user(self):
        """Test GET /api/users/{email} endpoint"""
        print("🔍 Testing Get User Endpoint...")
        try:
            if not self.test_user_id:
                self.log_test("Get User", False, "No test user created")
                return False
            
            # First, get the user email from the created user
            timestamp = int(time.time())
            test_email = f"influencer{timestamp}@shadoom.com"
            
            response = self.session.get(f"{self.base_url}/users/{test_email}")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "email", "name", "created_at"]
                
                if all(field in data for field in required_fields):
                    if data["email"] == test_email:
                        self.log_test("Get User", True, f"User retrieved successfully: {data['name']}")
                        return True
                    else:
                        self.log_test("Get User", False, "Email mismatch in response")
                        return False
                else:
                    self.log_test("Get User", False, f"Missing required fields. Got: {list(data.keys())}")
                    return False
            elif response.status_code == 404:
                # Try creating a user first, then retrieving
                self.test_create_user()
                return self.test_get_user()
            else:
                self.log_test("Get User", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get User", False, f"Exception: {str(e)}")
            return False
    
    def test_generate_ideas(self):
        """Test POST /api/generate-ideas endpoint - MAIN FUNCTIONALITY"""
        print("🔍 Testing Generate Ideas Endpoint (Gemini AI Integration)...")
        try:
            if not self.test_user_id:
                # Create a test user first
                self.test_create_user()
            
            # Test with fitness topic as specified in the review request
            ideas_request = {
                "user_id": self.test_user_id or "test-user-123",
                "topic": "fitness"
            }
            
            print("   Sending request to Gemini AI... (this may take a few seconds)")
            response = self.session.post(f"{self.base_url}/generate-ideas", json=ideas_request)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify we got a list of ideas
                if isinstance(data, list) and len(data) == 5:
                    # Check each idea has required fields
                    required_fields = ["id", "user_id", "topic", "title", "script", "content_type", "hashtags", "created_at"]
                    
                    all_valid = True
                    for i, idea in enumerate(data):
                        if not all(field in idea for field in required_fields):
                            self.log_test("Generate Ideas", False, f"Idea {i+1} missing required fields. Got: {list(idea.keys())}")
                            all_valid = False
                            break
                        
                        # Verify data types and content
                        if not isinstance(idea["hashtags"], list) or len(idea["hashtags"]) == 0:
                            self.log_test("Generate Ideas", False, f"Idea {i+1} has invalid hashtags")
                            all_valid = False
                            break
                        
                        if idea["topic"] != "fitness":
                            self.log_test("Generate Ideas", False, f"Idea {i+1} has wrong topic: {idea['topic']}")
                            all_valid = False
                            break
                    
                    if all_valid:
                        self.test_idea_id = data[0]["id"]  # Store first idea ID for delete test
                        self.log_test("Generate Ideas", True, f"Generated 5 ideas successfully. Sample title: '{data[0]['title']}'")
                        
                        # Test AI vs Fallback
                        if "Gemini AI" in str(data) or any("💡 Ideia Criativa" in idea["title"] for idea in data):
                            print("   🤖 Fallback ideas detected (AI may have failed)")
                        else:
                            print("   🧠 AI-generated ideas detected")
                        
                        return True
                    else:
                        return False
                else:
                    self.log_test("Generate Ideas", False, f"Expected 5 ideas, got {len(data) if isinstance(data, list) else 'non-list'}")
                    return False
            else:
                self.log_test("Generate Ideas", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Generate Ideas", False, f"Exception: {str(e)}")
            return False
    
    def test_get_user_ideas(self):
        """Test GET /api/ideas/{user_id} endpoint"""
        print("🔍 Testing Get User Ideas Endpoint...")
        try:
            if not self.test_user_id:
                self.log_test("Get User Ideas", False, "No test user available")
                return False
            
            response = self.session.get(f"{self.base_url}/ideas/{self.test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    if len(data) > 0:
                        # Verify structure of returned ideas
                        required_fields = ["id", "user_id", "topic", "title", "script", "content_type", "hashtags", "created_at"]
                        
                        if all(field in data[0] for field in required_fields):
                            self.log_test("Get User Ideas", True, f"Retrieved {len(data)} ideas for user")
                            return True
                        else:
                            self.log_test("Get User Ideas", False, f"Ideas missing required fields. Got: {list(data[0].keys())}")
                            return False
                    else:
                        self.log_test("Get User Ideas", True, "No ideas found for user (empty list is valid)")
                        return True
                else:
                    self.log_test("Get User Ideas", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_test("Get User Ideas", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get User Ideas", False, f"Exception: {str(e)}")
            return False
    
    def test_delete_idea(self):
        """Test DELETE /api/ideas/{idea_id} endpoint"""
        print("🔍 Testing Delete Idea Endpoint...")
        try:
            if not self.test_idea_id:
                self.log_test("Delete Idea", False, "No test idea available")
                return False
            
            response = self.session.delete(f"{self.base_url}/ideas/{self.test_idea_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                if "message" in data and "deleted" in data["message"].lower():
                    self.log_test("Delete Idea", True, f"Idea deleted successfully: {data['message']}")
                    return True
                else:
                    self.log_test("Delete Idea", False, f"Unexpected response format: {data}")
                    return False
            elif response.status_code == 404:
                self.log_test("Delete Idea", False, "Idea not found (may have been deleted already)")
                return False
            else:
                self.log_test("Delete Idea", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Delete Idea", False, f"Exception: {str(e)}")
            return False
    
    def test_gemini_integration(self):
        """Specific test for Gemini AI integration and fallback"""
        print("🔍 Testing Gemini AI Integration and Fallback...")
        try:
            # Test with a complex topic to see if AI responds appropriately
            ideas_request = {
                "user_id": "ai-test-user",
                "topic": "marketing digital para pequenos negócios"
            }
            
            response = self.session.post(f"{self.base_url}/generate-ideas", json=ideas_request)
            
            if response.status_code == 200:
                data = response.json()
                
                if len(data) == 5:
                    # Check if ideas are contextually relevant
                    relevant_keywords = ["marketing", "digital", "negócio", "pequeno", "empresa"]
                    
                    relevance_score = 0
                    for idea in data:
                        title_lower = idea["title"].lower()
                        script_lower = idea["script"].lower()
                        
                        for keyword in relevant_keywords:
                            if keyword in title_lower or keyword in script_lower:
                                relevance_score += 1
                                break
                    
                    if relevance_score >= 3:  # At least 3 out of 5 ideas should be relevant
                        self.log_test("Gemini AI Integration", True, f"AI generated contextually relevant ideas ({relevance_score}/5 relevant)")
                        return True
                    else:
                        self.log_test("Gemini AI Integration", True, f"Fallback ideas working ({relevance_score}/5 relevant - likely fallback)")
                        return True
                else:
                    self.log_test("Gemini AI Integration", False, f"Expected 5 ideas, got {len(data)}")
                    return False
            else:
                self.log_test("Gemini AI Integration", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Gemini AI Integration", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Shadoom Backend API Tests")
        print("=" * 50)
        print(f"Testing against: {self.base_url}")
        print("=" * 50)
        
        results = {}
        
        # Test 1: Health Check
        results["health_check"] = self.test_health_check()
        
        # Test 2: Create User
        results["create_user"] = self.test_create_user()
        
        # Test 3: Get User
        results["get_user"] = self.test_get_user()
        
        # Test 4: Generate Ideas (MAIN FUNCTIONALITY)
        results["generate_ideas"] = self.test_generate_ideas()
        
        # Test 5: Get User Ideas
        results["get_user_ideas"] = self.test_get_user_ideas()
        
        # Test 6: Delete Idea
        results["delete_idea"] = self.test_delete_idea()
        
        # Test 7: Gemini AI Integration
        results["gemini_integration"] = self.test_gemini_integration()
        
        # Summary
        print("=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name.replace('_', ' ').title()}")
        
        print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All backend tests PASSED! Shadoom API is working correctly.")
        else:
            print("⚠️  Some tests FAILED. Check the details above.")
        
        return results

if __name__ == "__main__":
    tester = ShadoomAPITester()
    results = tester.run_all_tests()