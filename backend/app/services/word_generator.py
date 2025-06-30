"""
Word-based short code generator for creating memorable, human-friendly URLs.
"""
import random
from typing import List

# Curated lists of pronounceable words
ADJECTIVES = [
    "blue", "red", "green", "bright", "dark", "light", "fast", "slow", "big", "small",
    "happy", "calm", "wild", "cool", "warm", "fresh", "smooth", "rough", "sharp", "soft",
    "quick", "lazy", "busy", "quiet", "loud", "deep", "high", "wide", "thin", "thick",
    "sweet", "sour", "hot", "cold", "new", "old", "young", "rich", "poor", "clean",
    "dirty", "empty", "full", "open", "closed", "free", "busy", "easy", "hard", "simple",
    "complex", "strong", "weak", "brave", "shy", "smart", "wise", "kind", "mean", "nice",
    "rude", "polite", "funny", "sad", "angry", "tired", "hungry", "thirsty", "sick", "healthy",
    "lucky", "unlucky", "safe", "risky", "cheap", "costly", "rare", "common", "special", "normal"
]

NOUNS = [
    "cat", "dog", "bird", "fish", "tree", "flower", "house", "car", "book", "phone",
    "table", "chair", "door", "window", "bridge", "road", "river", "mountain", "ocean", "lake",
    "sun", "moon", "star", "cloud", "rain", "snow", "fire", "water", "earth", "wind",
    "apple", "banana", "orange", "grape", "bread", "cake", "coffee", "tea", "milk", "cheese",
    "music", "song", "dance", "movie", "game", "sport", "ball", "bike", "train", "plane",
    "key", "box", "bag", "hat", "shoe", "shirt", "dress", "watch", "ring", "gift",
    "paper", "pen", "pencil", "brush", "paint", "color", "photo", "camera", "mirror", "glass",
    "heart", "mind", "soul", "dream", "hope", "love", "peace", "joy", "smile", "laugh"
]

# Action words for variety
VERBS = [
    "run", "walk", "jump", "fly", "swim", "dance", "sing", "play", "work", "sleep",
    "eat", "drink", "read", "write", "draw", "paint", "build", "make", "create", "fix",
    "help", "teach", "learn", "think", "dream", "wish", "hope", "love", "like", "want",
    "give", "take", "buy", "sell", "find", "lose", "win", "fail", "start", "stop",
    "open", "close", "push", "pull", "lift", "drop", "throw", "catch", "hit", "miss"
]


class WordCodeGenerator:
    """Generates memorable word-based short codes."""
    
    @staticmethod
    def generate_word_code() -> str:
        """
        Generate a memorable short code using words.
        
        Patterns:
        - adjective + noun (e.g., "bluecats", "fastbird") 
        - verb + noun (e.g., "runbird", "jumpfish")
        - adjective + verb (e.g., "quickrun", "brightfly")
        
        Returns:
            A memorable 6-12 character word-based code
        """
        pattern = random.choice(['adj_noun', 'verb_noun', 'adj_verb'])
        
        if pattern == 'adj_noun':
            word1 = random.choice(ADJECTIVES)
            word2 = random.choice(NOUNS)
        elif pattern == 'verb_noun':
            word1 = random.choice(VERBS)
            word2 = random.choice(NOUNS)
        else:  # adj_verb
            word1 = random.choice(ADJECTIVES)
            word2 = random.choice(VERBS)
        
        # Combine words
        code = word1 + word2
        
        # Ensure it's not too long (max 12 characters for readability)
        if len(code) > 12:
            # Try shorter words
            return WordCodeGenerator._generate_short_combination()
        
        return code
    
    @staticmethod
    def _generate_short_combination() -> str:
        """Generate a combination with shorter words."""
        # Filter for shorter words
        short_adjectives = [w for w in ADJECTIVES if len(w) <= 5]
        short_nouns = [w for w in NOUNS if len(w) <= 5]
        short_verbs = [w for w in VERBS if len(w) <= 5]
        
        pattern = random.choice(['adj_noun', 'verb_noun', 'adj_verb'])
        
        if pattern == 'adj_noun':
            word1 = random.choice(short_adjectives)
            word2 = random.choice(short_nouns)
        elif pattern == 'verb_noun':
            word1 = random.choice(short_verbs)
            word2 = random.choice(short_nouns)
        else:  # adj_verb
            word1 = random.choice(short_adjectives)
            word2 = random.choice(short_verbs)
        
        return word1 + word2
    
    @staticmethod
    def generate_numbered_code() -> str:
        """
        Generate a word + number combination for extra variety.
        
        Returns:
            A code like "bluecat42" or "fastrun7"
        """
        base_code = WordCodeGenerator.generate_word_code()
        number = random.randint(1, 99)
        
        # Keep it reasonable length
        if len(base_code) > 8:
            base_code = WordCodeGenerator._generate_short_combination()
        
        return f"{base_code}{number}"
    
    @staticmethod
    def is_appropriate(code: str) -> bool:
        """
        Check if a generated code is appropriate (no unintended words).
        This is a basic check - you could expand this with a word filter.
        """
        # Basic inappropriate word filter (expand as needed)
        inappropriate_substrings = ['hell', 'damn', 'hate', 'kill', 'die', 'sex']
        code_lower = code.lower()
        
        for word in inappropriate_substrings:
            if word in code_lower:
                return False
        
        return True
