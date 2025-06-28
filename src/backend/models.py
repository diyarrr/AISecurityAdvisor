class User:
    # Define ranks and their XP thresholds
    RANKS = {
        1: {"name": "Security Novice", "threshold": 0},
        2: {"name": "Security Apprentice", "threshold": 100},
        3: {"name": "Security Adept", "threshold": 250},
        4: {"name": "Security Expert", "threshold": 500},
        5: {"name": "Security Master", "threshold": 1000}
    }
    
    # Define topic access by rank
    TOPIC_ACCESS = {
        1: ["phishing", "passwords", "basic security", "malware", "social engineering"],
        2: ["data protection", "email security", "device security", "secure browsing"],
        3: ["network security", "encryption", "authentication", "security policies"],
        4: ["incident response", "security audits", "risk assessment", "compliance"],
        5: ["penetration testing", "advanced threats", "security architecture", "zero trust"]
    }
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.xp = 0
        self.rank = 1
        self.interactions = 0
        self.history = []  # Store previous interactions
    
    def add_xp(self, points):
        """Add experience points and update rank if necessary"""
        self.xp = max(0, self.xp + points)
        self.update_rank()
        return self.xp
    
    def update_rank(self):
        thresholds = {
            1: 0,
            2: 100,
            3: 250,
            4: 500,
            5: 1000
        }

        current_threshold = thresholds.get(self.rank, 0)

        # Prevent rank down: if XP < threshold, cap it to threshold minimum
        if self.xp < current_threshold:
            self.xp = current_threshold
            return

        # Normal rank-up behavior
        for rank, threshold in sorted(thresholds.items()):
            if self.xp >= threshold:
                self.rank = rank

        # Optionally assign readable rank name
        self.rank_name = {
            1: "Security Novice",
            2: "Security Explorer",
            3: "Security Practitioner",
            4: "Security Defender",
            5: "Security Expert"
        }.get(self.rank, "Unknown")

    
    def can_access_topic(self, topic):
        """Check if user can access a given topic based on rank"""
        allowed_topics = []
        for rank in range(1, self.rank + 1):
            allowed_topics.extend(self.TOPIC_ACCESS.get(rank, []))
        
        # Simple keyword matching (in production, use more sophisticated topic detection)
        return any(t in topic.lower() for t in allowed_topics)
    
    def add_interaction(self, query, response):
        """Record user interaction"""
        self.interactions += 1
        self.history.append({"query": query, "response": response})
    
    def to_dict(self):
        """Return user data as dictionary"""
        return {
            "user_id": self.user_id,
            "xp": self.xp,
            "rank": self.rank,
            "rank_name": self.RANKS[self.rank]["name"],
            "next_rank": self.RANKS.get(self.rank + 1, {"name": "Maximum Rank Achieved", "threshold": "N/A"}),
            "interactions": self.interactions
        }