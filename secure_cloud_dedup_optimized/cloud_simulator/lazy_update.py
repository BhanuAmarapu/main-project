"""
Lazy update strategy for KEK tree
Defers key updates for better performance
"""
from datetime import datetime, timedelta
from .kek_tree import KEKTree


class LazyUpdateManager:
    """Lazy update strategy for efficient key management"""
    
    def __init__(self, kek_tree, batch_size=10, update_interval_minutes=5):
        """
        Initialize lazy update manager
        
        Args:
            kek_tree: KEKTree instance
            batch_size: Number of updates to batch
            update_interval_minutes: Time interval for batched updates
        """
        self.kek_tree = kek_tree
        self.batch_size = batch_size
        self.update_interval = timedelta(minutes=update_interval_minutes)
        self.pending_updates = []
        self.last_update_time = datetime.utcnow()
    
    def queue_update(self, node_id, new_key_hash):
        """
        Queue a key update
        
        Args:
            node_id: Node ID to update
            new_key_hash: New key hash
        """
        self.pending_updates.append({
            'node_id': node_id,
            'key_hash': new_key_hash,
            'queued_at': datetime.utcnow()
        })
        
        # Check if we should flush
        if self._should_flush():
            self.flush_updates()
    
    def _should_flush(self):
        """Check if updates should be flushed"""
        # Flush if batch size reached
        if len(self.pending_updates) >= self.batch_size:
            return True
        
        # Flush if time interval passed
        if datetime.utcnow() - self.last_update_time >= self.update_interval:
            return True
        
        return False
    
    def flush_updates(self):
        """
        Flush all pending updates
        
        Returns:
            Number of updates applied
        """
        if not self.pending_updates:
            return 0
        
        # Group updates by node to avoid redundant updates
        updates_by_node = {}
        for update in self.pending_updates:
            node_id = update['node_id']
            # Keep only the latest update for each node
            if node_id not in updates_by_node or update['queued_at'] > updates_by_node[node_id]['queued_at']:
                updates_by_node[node_id] = update
        
        # Apply updates
        total_updated = 0
        for update in updates_by_node.values():
            updated_nodes = self.kek_tree.update_key(update['node_id'], update['key_hash'])
            total_updated += len(updated_nodes)
        
        # Clear pending updates
        self.pending_updates = []
        self.last_update_time = datetime.utcnow()
        
        return total_updated
    
    def force_flush(self):
        """Force immediate flush of all pending updates"""
        return self.flush_updates()
    
    def get_pending_count(self):
        """Get number of pending updates"""
        return len(self.pending_updates)
    
    def get_stats(self):
        """Get lazy update statistics"""
        return {
            'pending_updates': len(self.pending_updates),
            'batch_size': self.batch_size,
            'update_interval_minutes': self.update_interval.total_seconds() / 60,
            'last_update': self.last_update_time.isoformat(),
            'time_since_last_update_seconds': (datetime.utcnow() - self.last_update_time).total_seconds()
        }
