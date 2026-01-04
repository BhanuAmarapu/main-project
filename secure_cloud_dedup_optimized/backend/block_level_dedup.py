"""
Block-level deduplication module
Supports both fixed-size and variable-size chunking
"""
import os
import hashlib
from .models import db, Block, File
from .encryption import encrypt_data, decrypt_data
from .config import Config


class BlockLevelDedup:
    """Block-level deduplication handler"""
    
    def __init__(self, block_size=None, use_variable=None):
        """
        Initialize block-level deduplication
        
        Args:
            block_size: Size of blocks in bytes (default: from config)
            use_variable: Use variable-size blocks (default: from config)
        """
        self.block_size = block_size or Config.BLOCK_SIZE
        self.use_variable = use_variable if use_variable is not None else Config.USE_VARIABLE_BLOCKS
    
    def chunk_file_fixed(self, file_path):
        """
        Chunk file into fixed-size blocks
        
        Args:
            file_path: Path to file
        
        Returns:
            List of (block_data, block_hash) tuples
        """
        blocks = []
        
        with open(file_path, 'rb') as f:
            while True:
                block_data = f.read(self.block_size)
                if not block_data:
                    break
                
                block_hash = hashlib.sha256(block_data).hexdigest()
                blocks.append((block_data, block_hash))
        
        return blocks
    
    def chunk_file_variable(self, file_path, window_size=48):
        """
        Chunk file into variable-size blocks using Rabin fingerprinting
        (Simplified version)
        
        Args:
            file_path: Path to file
            window_size: Rolling hash window size
        
        Returns:
            List of (block_data, block_hash) tuples
        """
        blocks = []
        current_block = bytearray()
        
        with open(file_path, 'rb') as f:
            data = f.read()
        
        for i, byte in enumerate(data):
            current_block.append(byte)
            
            # Simple boundary detection (in production, use proper Rabin fingerprinting)
            if len(current_block) >= self.block_size:
                # Check if we should create a boundary
                if len(current_block) >= self.block_size * 2 or i == len(data) - 1:
                    block_data = bytes(current_block)
                    block_hash = hashlib.sha256(block_data).hexdigest()
                    blocks.append((block_data, block_hash))
                    current_block = bytearray()
        
        # Add remaining data as final block
        if current_block:
            block_data = bytes(current_block)
            block_hash = hashlib.sha256(block_data).hexdigest()
            blocks.append((block_data, block_hash))
        
        return blocks
    
    def store_blocks(self, file_id, blocks):
        """
        Store blocks with deduplication
        
        Args:
            file_id: File ID
            blocks: List of (block_data, block_hash) tuples
        
        Returns:
            dict with storage stats
        """
        blocks_stored = 0
        blocks_deduplicated = 0
        bytes_saved = 0
        
        for block_data, block_hash in blocks:
            # Check if block already exists
            existing_block = Block.query.filter_by(block_hash=block_hash).first()
            
            if existing_block:
                # Block exists, just increment reference count
                existing_block.reference_count += 1
                blocks_deduplicated += 1
                bytes_saved += len(block_data)
            else:
                # New block, store it
                block_path = os.path.join(Config.BLOCKS_DIR, f"{block_hash}.blk")
                
                # Encrypt block data
                encrypted_data = encrypt_data(block_data)
                
                with open(block_path, 'wb') as f:
                    f.write(encrypted_data)
                
                # Create block record
                new_block = Block(
                    block_hash=block_hash,
                    block_size=len(block_data),
                    stored_path=block_path,
                    file_id=file_id,
                    reference_count=1
                )
                
                db.session.add(new_block)
                blocks_stored += 1
        
        db.session.commit()
        
        # Update file record
        file = File.query.get(file_id)
        if file:
            file.has_blocks = True
            db.session.commit()
        
        return {
            'total_blocks': len(blocks),
            'new_blocks': blocks_stored,
            'deduplicated_blocks': blocks_deduplicated,
            'bytes_saved': bytes_saved,
            'dedup_ratio': (bytes_saved / sum([len(b[0]) for b in blocks])) * 100 if blocks else 0
        }
    
    def reconstruct_file(self, file_id, output_path):
        """
        Reconstruct file from blocks
        
        Args:
            file_id: File ID
            output_path: Path to output file
        
        Returns:
            bool: True if successful
        """
        # Get all blocks for this file
        blocks = Block.query.filter_by(file_id=file_id).order_by(Block.id).all()
        
        if not blocks:
            return False
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Reconstruct file
        with open(output_path, 'wb') as out_file:
            for block in blocks:
                # Read encrypted block
                with open(block.stored_path, 'rb') as f:
                    encrypted_data = f.read()
                
                # Decrypt block
                decrypted_data = decrypt_data(encrypted_data)
                
                # Write to output
                out_file.write(decrypted_data)
        
        return True
    
    def get_block_stats(self):
        """Get block-level deduplication statistics"""
        total_blocks = Block.query.count()
        total_references = db.session.query(db.func.sum(Block.reference_count)).scalar() or 0
        
        deduplicated_blocks = total_references - total_blocks
        
        total_size = db.session.query(db.func.sum(Block.block_size)).scalar() or 0
        
        # Calculate space saved
        space_saved = 0
        if total_blocks > 0:
            blocks = Block.query.all()
            for block in blocks:
                if block.reference_count > 1:
                    space_saved += block.block_size * (block.reference_count - 1)
        
        return {
            'total_unique_blocks': total_blocks,
            'total_block_references': total_references,
            'deduplicated_blocks': deduplicated_blocks,
            'space_saved_bytes': space_saved,
            'space_saved_mb': space_saved / (1024 * 1024),
            'total_storage_bytes': total_size,
            'dedup_ratio': (space_saved / (total_size + space_saved)) * 100 if (total_size + space_saved) > 0 else 0
        }
