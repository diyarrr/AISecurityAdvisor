import os
import openai # CHANGED: No longer from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv(dotenv_path="config/.env", override=True)

class SecurityChatbot:
    def __init__(self, retriever):
        """Initialize the security chatbot with a document retriever"""
        self.retriever = retriever
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        # CHANGED: Set the API key on the module level
        openai.api_key = self.openai_api_key

        # Topic keywords for basic classification
        # In production, use a more sophisticated topic classification system
        self.topic_keywords = {
            "phishing": ["phishing", "scam", "fake email", "suspicious link"],
            "passwords": ["password", "credentials", "authentication", "login"],
            "encryption": ["encryption", "encrypt", "cipher", "cryptography"],
            "network": ["network", "wifi", "router", "firewall", "vpn"],
            "incident_response": ["incident", "breach", "attack", "response", "compromise"],
            "penetration_testing": ["pentest", "penetration", "ethical hacking", "vulnerability scan"],
            "malware": ["malware", "virus", "trojan", "ransomware"],
            "social engineering": ["social engineering", "impersonation", "baiting", "pretexting"],
            "data protection": ["data protection", "gdpr", "data loss", "privacy policy"],
            "email security": ["email security", "spoofing", "dmarc", "spam"],
            "device security": ["device security", "mobile protection", "laptop safety"],
            "secure browsing": ["https", "browser safety", "secure website", "ssl"],
            "authentication": ["authentication", "2fa", "mfa", "identity verification"],
            "security policies": ["security policies", "acceptable use", "access control"],
            "security audits": ["audit", "security audit", "compliance check"],
            "risk assessment": ["risk assessment", "risk analysis", "vulnerability scoring"],
            "compliance": ["compliance", "regulations", "laws", "ISO 27001"],
            "advanced threats": ["apt", "zero-day", "stealth attack"],
            "security architecture": ["architecture", "security design", "defense in depth"],
            "zero trust": ["zero trust", "never trust", "verify always"]
        }


        # Map topics to minimum required ranks
        self.topic_ranks = {
            "phishing": 1,
            "passwords": 1,
            "basic security": 1,
            "malware": 1,
            "social engineering": 1,
            "data protection": 2,
            "email security": 2,
            "device security": 2,
            "secure browsing": 2,
            "network": 3,
            "encryption": 3,
            "authentication": 3,
            "security policies": 3,
            "incident_response": 4,
            "security audits": 4,
            "risk assessment": 4,
            "compliance": 4,
            "penetration_testing": 5,
            "advanced threats": 5,
            "security architecture": 5,
            "zero trust": 5
        }

    def check_topic_access(self, query, user_rank):
        """Check if user has access to the topic based on their rank"""
        query_lower = query.lower()

        # Identify the topic from the query
        detected_topics = []
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_topics.append(topic)

        # If no specific topic is detected, default to basic security (rank 1)
        if not detected_topics:
            return True

        # Check if user rank is sufficient for all detected topics
        for topic in detected_topics:
            required_rank = self.topic_ranks.get(topic, 1)  # Default to rank 1 if not specified
            if user_rank < required_rank:
                return False

        return True

    def generate_response(self, query, user_rank):
        """Generate a response to the user's query based on their rank"""
        # Retrieve relevant documents
        retrieved_context = self.retriever.query_documents(query)

        # Create prompt with different complexity based on user rank
        system_messages = {
            1: "You are a Security Advisor Chatbot helping users learn about basic cybersecurity concepts. Use simple language and avoid technical jargon. Focus on practical tips for beginners.",
            2: "You are a Security Advisor Chatbot helping users improve their cybersecurity knowledge. Use straightforward explanations with some technical terms defined when used.",
            3: "You are a Security Advisor Chatbot for users with intermediate cybersecurity knowledge. You can use technical terminology and provide detailed explanations.",
            4: "You are a Security Advisor Chatbot for security-proficient users. Provide in-depth technical explanations and advanced security concepts.",
            5: "You are a Security Advisor Chatbot for security experts. Use advanced technical language and detailed explanations about sophisticated security concepts and strategies."
        }

        system_message = system_messages.get(user_rank, system_messages[1])

        # Add specific instructions based on rank
        rank_specific_instructions = {
            1: "Remember to emphasize the importance of basic security practices like strong passwords and being cautious of suspicious emails.",
            2: "You can introduce concepts like two-factor authentication and the importance of software updates.",
            3: "You can discuss network security concepts and basic security policies.",
            4: "You can cover incident response procedures and security auditing techniques.",
            5: "You can discuss advanced threat models, penetration testing techniques, and sophisticated security architectures."
        }

        system_message += " " + rank_specific_instructions.get(user_rank, "")

        # Add retrieved context to the prompt
        if retrieved_context:
            system_message += "\n\nUse the following information to inform your answer if relevant:\n" + retrieved_context

        # Call the LLM API
        # CHANGED: The API call syntax is different for openai<1.0.0
        response = openai.ChatCompletion.create(
            model="gpt-4o", # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": query}
            ],
            max_tokens=1000,
            temperature=0.7
        )

        return response.choices[0].message.content

    def generate_followup_question(self, answer):
        """Generate a quiz question from the given answer"""
        followup_prompt = (
            "Based on the following information, generate one multiple-choice question "
            "with four options and indicate the correct answer.\n\n"
            f"{answer}\n\n"
            "Format the response like this:\n"
            "Question: ...\nOptions:\na) ...\nb) ...\nc) ...\nd) ...\nAnswer: ..."
        )

        # CHANGED: The API call syntax is different here as well
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a quiz generator for cybersecurity topics."},
                {"role": "user", "content": followup_prompt}
            ],
            max_tokens=300,
            temperature=0.5
        )
        return response.choices[0].message.content