"""
KEK (Key Encryption Key) Tree implementation
Hierarchical key management for efficient key updates
"""
import hashlib
import os
from backend.models import db, KEKTreeNode
from datetime import datetime


class KEKTree:
    """Key Encryption Key tree for hierarchical key management"""
    
    def __init__(self, branching_factor=4):
        """
        Initialize KEK tree
        
        Args:
            branching_factor: Number of children per node
        """
        self.branching_factor = branching_factor
        self.root = None
    
    def _generate_key_hash(self, data):
        """Generate key hash"""
        return hashlib.sha256(data.encode() if isinstance(data, str) else data).hexdigest()
    
    def _generate_node_id(self, level, index):
        """Generate unique node ID"""
        return f"L{level}_N{index}"
    
    def create_tree(self, num_leaves):
        """
        Create KEK tree with specified number of leaves
        
        Args:
            num_leaves: Number of leaf nodes
        
        Returns:
            Root node
        """
        import math
        
        # Calculate tree height
        height = math.ceil(math.log(num_leaves, self.branching_factor)) + 1
        
        # Create root
        root_id = self._generate_node_id(0, 0)
        root_key = os.urandom(32)  # 256-bit key
        root_hash = self._generate_key_hash(root_key)
        
        root = KEKTreeNode(
            node_id=root_id,
            key_hash=root_hash,
            level=0,
            is_leaf=False
        )
        
        db.session.add(root)
        db.session.commit()
        
        self.root = root
        
        # Create tree levels
        current_level_nodes = [root]
        
        for level in range(1, height):
            next_level_nodes = []
            node_index = 0
            
            for parent in current_level_nodes:
                for i in range(self.branching_factor):
                    if level == height - 1 and node_index >= num_leaves:
                        break
                    
                    node_id = self._generate_node_id(level, node_index)
                    node_key = os.urandom(32)
                    node_hash = self._generate_key_hash(node_key)
                    
                    is_leaf = (level == height - 1)
                    
                    node = KEKTreeNode(
                        node_id=node_id,
                        parent_id=parent.node_id,
                        key_hash=node_hash,
                        level=level,
                        is_leaf=is_leaf
                    )
                    
                    db.session.add(node)
                    next_level_nodes.append(node)
                    node_index += 1
                
                if level == height - 1 and node_index >= num_leaves:
                    break
            
            db.session.commit()
            current_level_nodes = next_level_nodes
        
        return root
    
    def update_key(self, node_id, new_key_hash):
        """
        Update key for a node
        
        Args:
            node_id: Node ID to update
            new_key_hash: New key hash
        
        Returns:
            List of updated node IDs
        """
        node = KEKTreeNode.query.filter_by(node_id=node_id).first()
        
        if not node:
            return []
        
        # Update node
        node.key_hash = new_key_hash
        node.updated_at = datetime.utcnow()
        
        updated_nodes = [node_id]
        
        # Propagate update to parent (if not root)
        if node.parent_id:
            parent_updates = self.update_key(node.parent_id, new_key_hash)
            updated_nodes.extend(parent_updates)
        
        db.session.commit()
        
        return updated_nodes
    
    def get_path_to_root(self, node_id):
        """
        Get path from node to root
        
        Args:
            node_id: Starting node ID
        
        Returns:
            List of node IDs from node to root
        """
        path = []
        current_id = node_id
        
        while current_id:
            node = KEKTreeNode.query.filter_by(node_id=current_id).first()
            if not node:
                break
            
            path.append(current_id)
            current_id = node.parent_id
        
        return path
    
    def get_subtree_nodes(self, node_id):
        """
        Get all nodes in subtree
        
        Args:
            node_id: Root of subtree
        
        Returns:
            List of node IDs
        """
        nodes = [node_id]
        
        # Get all children
        children = KEKTreeNode.query.filter_by(parent_id=node_id).all()
        
        for child in children:
            subtree = self.get_subtree_nodes(child.node_id)
            nodes.extend(subtree)
        
        return nodes
    
    def get_tree_stats(self):
        """Get KEK tree statistics"""
        total_nodes = KEKTreeNode.query.count()
        leaf_nodes = KEKTreeNode.query.filter_by(is_leaf=True).count()
        internal_nodes = total_nodes - leaf_nodes
        
        # Get tree height
        max_level = db.session.query(db.func.max(KEKTreeNode.level)).scalar() or 0
        
        return {
            'total_nodes': total_nodes,
            'leaf_nodes': leaf_nodes,
            'internal_nodes': internal_nodes,
            'tree_height': max_level + 1,
            'branching_factor': self.branching_factor
        }
    
    def visualize_tree(self, max_depth=3):
        """
        Create a simple text visualization of the tree
        
        Args:
            max_depth: Maximum depth to visualize
        
        Returns:
            String representation
        """
        if not self.root:
            root = KEKTreeNode.query.filter_by(level=0).first()
            if not root:
                return "Empty tree"
            self.root = root
        
        def _visualize_node(node, depth=0, prefix=""):
            if depth > max_depth:
                return ""
            
            result = f"{prefix}{node.node_id} (L{node.level})\n"
            
            children = KEKTreeNode.query.filter_by(parent_id=node.node_id).all()
            
            for i, child in enumerate(children):
                is_last = (i == len(children) - 1)
                child_prefix = prefix + ("└── " if is_last else "├── ")
                next_prefix = prefix + ("    " if is_last else "│   ")
                result += _visualize_node(child, depth + 1, child_prefix)
            
            return result
        
        return _visualize_node(self.root)
