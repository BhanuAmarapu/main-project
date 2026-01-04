"""
Optimized compressed Bloom filter
Uses compression for better memory efficiency
"""
import zlib
from .bloom_filter import BloomFilter


class OptimizedBloomFilter(BloomFilter):
    """Compressed Bloom filter with persistence support"""
    
    def __init__(self, size=None, hash_count=None, false_positive_rate=None, compression_level=6):
        """
        Initialize optimized Bloom filter
        
        Args:
            size: Size of bit array
            hash_count: Number of hash functions
            false_positive_rate: Desired false positive rate
            compression_level: Zlib compression level (1-9)
        """
        super().__init__(size, hash_count, false_positive_rate)
        self.compression_level = compression_level
    
    def to_compressed_bytes(self):
        """
        Serialize and compress Bloom filter
        
        Returns:
            Compressed bytes
        """
        raw_bytes = self.to_bytes()
        compressed = zlib.compress(raw_bytes, level=self.compression_level)
        return compressed
    
    @classmethod
    def from_compressed_bytes(cls, compressed_data, size, hash_count, compression_level=6):
        """
        Deserialize from compressed bytes
        
        Args:
            compressed_data: Compressed bytes
            size: Bit array size
            hash_count: Number of hash functions
            compression_level: Compression level
        
        Returns:
            OptimizedBloomFilter instance
        """
        raw_data = zlib.decompress(compressed_data)
        bf = cls(size=size, hash_count=hash_count, compression_level=compression_level)
        
        # Convert bytes to bit array
        for i, byte in enumerate(raw_data):
            for j in range(8):
                if i * 8 + j < size:
                    bf.bit_array[i * 8 + j] = 1 if (byte & (1 << j)) else 0
        
        # Estimate item count
        bits_set = sum(bf.bit_array)
        if bits_set > 0:
            try:
                import math
                bf.item_count = int(-(size / hash_count) * math.log(1 - bits_set / size))
            except:
                bf.item_count = 0
        
        return bf
    
    def save_to_db(self):
        """
        Save Bloom filter state to database
        
        Returns:
            BloomFilterState record
        """
        from backend.models import db, BloomFilterState
        
        compressed_data = self.to_compressed_bytes()
        
        # Check if state exists
        state = BloomFilterState.query.first()
        
        if state:
            # Update existing
            state.filter_data = compressed_data
            state.size = self.size
            state.hash_count = self.hash_count
            state.item_count = self.item_count
        else:
            # Create new
            state = BloomFilterState(
                filter_data=compressed_data,
                size=self.size,
                hash_count=self.hash_count,
                item_count=self.item_count
            )
            db.session.add(state)
        
        db.session.commit()
        return state
    
    @classmethod
    def load_from_db(cls):
        """
        Load Bloom filter state from database
        
        Returns:
            OptimizedBloomFilter instance or None
        """
        from backend.models import BloomFilterState
        
        state = BloomFilterState.query.first()
        
        if not state:
            return None
        
        return cls.from_compressed_bytes(
            state.filter_data,
            state.size,
            state.hash_count
        )
    
    def get_compression_stats(self):
        """Get compression statistics"""
        raw_bytes = self.to_bytes()
        compressed_bytes = self.to_compressed_bytes()
        
        compression_ratio = len(raw_bytes) / len(compressed_bytes) if len(compressed_bytes) > 0 else 1
        
        return {
            'raw_size_bytes': len(raw_bytes),
            'compressed_size_bytes': len(compressed_bytes),
            'compression_ratio': round(compression_ratio, 2),
            'space_saved_bytes': len(raw_bytes) - len(compressed_bytes),
            'space_saved_percent': round((1 - len(compressed_bytes) / len(raw_bytes)) * 100, 2) if len(raw_bytes) > 0 else 0
        }
