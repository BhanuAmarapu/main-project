"""
Basic Bloom filter implementation
Probabilistic data structure for membership testing
"""
import hashlib
import math


class BloomFilter:
    """Basic Bloom filter for fast duplicate detection"""
    
    def __init__(self, size=None, hash_count=None, false_positive_rate=None):
        """
        Initialize Bloom filter
        
        Args:
            size: Size of bit array (default: from config)
            hash_count: Number of hash functions (default: from config)
            false_positive_rate: Desired false positive rate (default: 0.01)
        """
        from backend.config import Config
        
        if false_positive_rate and not size:
            # Calculate optimal size based on false positive rate
            # Assuming expected number of elements
            expected_elements = 10000
            size = self._optimal_size(expected_elements, false_positive_rate)
            hash_count = self._optimal_hash_count(size, expected_elements)
        
        self.size = size or Config.BLOOM_FILTER_SIZE
        self.hash_count = hash_count or Config.BLOOM_FILTER_HASH_COUNT
        self.bit_array = [0] * self.size
        self.item_count = 0
    
    def _optimal_size(self, n, p):
        """
        Calculate optimal bit array size
        
        Args:
            n: Expected number of elements
            p: Desired false positive rate
        
        Returns:
            Optimal size
        """
        m = -(n * math.log(p)) / (math.log(2) ** 2)
        return int(m)
    
    def _optimal_hash_count(self, m, n):
        """
        Calculate optimal number of hash functions
        
        Args:
            m: Bit array size
            n: Expected number of elements
        
        Returns:
            Optimal hash count
        """
        k = (m / n) * math.log(2)
        return int(k)
    
    def _hash(self, item, seed):
        """
        Generate hash for item with seed
        
        Args:
            item: Item to hash
            seed: Hash seed
        
        Returns:
            Hash value
        """
        data = f"{item}:{seed}".encode()
        hash_value = int(hashlib.sha256(data).hexdigest(), 16)
        return hash_value % self.size
    
    def add(self, item):
        """
        Add item to Bloom filter
        
        Args:
            item: Item to add
        """
        for i in range(self.hash_count):
            index = self._hash(item, i)
            self.bit_array[index] = 1
        
        self.item_count += 1
    
    def contains(self, item):
        """
        Check if item might be in the filter
        
        Args:
            item: Item to check
        
        Returns:
            bool: True if item might be present (with false positive rate)
        """
        for i in range(self.hash_count):
            index = self._hash(item, i)
            if self.bit_array[index] == 0:
                return False
        
        return True
    
    def get_false_positive_rate(self):
        """
        Calculate current false positive rate
        
        Returns:
            Estimated false positive rate
        """
        if self.item_count == 0:
            return 0.0
        
        # Formula: (1 - e^(-kn/m))^k
        # where k = hash_count, n = item_count, m = size
        k = self.hash_count
        n = self.item_count
        m = self.size
        
        try:
            rate = (1 - math.exp(-k * n / m)) ** k
            return rate
        except:
            return 0.0
    
    def get_stats(self):
        """Get Bloom filter statistics"""
        bits_set = sum(self.bit_array)
        fill_ratio = bits_set / self.size if self.size > 0 else 0
        
        return {
            'size': self.size,
            'hash_count': self.hash_count,
            'item_count': self.item_count,
            'bits_set': bits_set,
            'fill_ratio': round(fill_ratio, 4),
            'false_positive_rate': round(self.get_false_positive_rate(), 6)
        }
    
    def clear(self):
        """Clear the Bloom filter"""
        self.bit_array = [0] * self.size
        self.item_count = 0
    
    def to_bytes(self):
        """
        Serialize Bloom filter to bytes
        
        Returns:
            bytes representation
        """
        # Convert bit array to bytes
        byte_array = bytearray()
        
        for i in range(0, len(self.bit_array), 8):
            byte = 0
            for j in range(8):
                if i + j < len(self.bit_array) and self.bit_array[i + j]:
                    byte |= (1 << j)
            byte_array.append(byte)
        
        return bytes(byte_array)
    
    @classmethod
    def from_bytes(cls, data, size, hash_count):
        """
        Deserialize Bloom filter from bytes
        
        Args:
            data: Bytes data
            size: Bit array size
            hash_count: Number of hash functions
        
        Returns:
            BloomFilter instance
        """
        bf = cls(size=size, hash_count=hash_count)
        
        # Convert bytes to bit array
        for i, byte in enumerate(data):
            for j in range(8):
                if i * 8 + j < size:
                    bf.bit_array[i * 8 + j] = 1 if (byte & (1 << j)) else 0
        
        # Count items (approximate)
        bits_set = sum(bf.bit_array)
        if bits_set > 0:
            # Estimate item count from fill ratio
            # n ≈ -(m/k) * ln(1 - X/m)
            # where X = bits_set
            try:
                bf.item_count = int(-(size / hash_count) * math.log(1 - bits_set / size))
            except:
                bf.item_count = 0
        
        return bf
