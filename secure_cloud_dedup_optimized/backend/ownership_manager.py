"""
Ownership management module
"""
from .models import db, Ownership, File, User
from datetime import datetime


class OwnershipManager:
    """Manage file ownership and access control"""
    
    def __init__(self):
        """Initialize ownership manager"""
        pass
    
    def grant_ownership(self, user_id, file_id, verification_method='upload'):
        """
        Grant ownership of a file to a user
        
        Args:
            user_id: User ID
            file_id: File ID
            verification_method: Method of verification
        
        Returns:
            Ownership record
        """
        # Check if ownership already exists
        existing = Ownership.query.filter_by(
            user_id=user_id,
            file_id=file_id
        ).first()
        
        if existing:
            return existing
        
        # Create new ownership record
        ownership = Ownership(
            user_id=user_id,
            file_id=file_id,
            verification_method=verification_method
        )
        
        db.session.add(ownership)
        db.session.commit()
        
        return ownership
    
    def verify_ownership(self, user_id, file_id):
        """
        Verify if user owns a file
        
        Args:
            user_id: User ID
            file_id: File ID
        
        Returns:
            bool: True if user owns the file
        """
        ownership = Ownership.query.filter_by(
            user_id=user_id,
            file_id=file_id
        ).first()
        
        return ownership is not None
    
    def get_user_files(self, user_id):
        """
        Get all files owned by a user
        
        Args:
            user_id: User ID
        
        Returns:
            List of File objects
        """
        ownerships = Ownership.query.filter_by(user_id=user_id).all()
        file_ids = [o.file_id for o in ownerships]
        files = File.query.filter(File.id.in_(file_ids)).all()
        
        return files
    
    def get_file_owners(self, file_id):
        """
        Get all users who own a file
        
        Args:
            file_id: File ID
        
        Returns:
            List of User objects
        """
        ownerships = Ownership.query.filter_by(file_id=file_id).all()
        user_ids = [o.user_id for o in ownerships]
        users = User.query.filter(User.id.in_(user_ids)).all()
        
        return users
    
    def revoke_ownership(self, user_id, file_id):
        """
        Revoke ownership of a file from a user
        
        Args:
            user_id: User ID
            file_id: File ID
        
        Returns:
            bool: True if revoked successfully
        """
        ownership = Ownership.query.filter_by(
            user_id=user_id,
            file_id=file_id
        ).first()
        
        if ownership:
            db.session.delete(ownership)
            
            # Update file reference count
            file = File.query.get(file_id)
            if file:
                file.reference_count = max(0, file.reference_count - 1)
            
            db.session.commit()
            return True
        
        return False
    
    def share_file(self, owner_id, recipient_id, file_id):
        """
        Share a file with another user
        
        Args:
            owner_id: Owner user ID
            recipient_id: Recipient user ID
            file_id: File ID
        
        Returns:
            dict with result
        """
        # Verify owner has ownership
        if not self.verify_ownership(owner_id, file_id):
            return {
                'success': False,
                'error': 'You do not own this file'
            }
        
        # Grant ownership to recipient
        ownership = self.grant_ownership(recipient_id, file_id, verification_method='shared')
        
        # Update file reference count
        file = File.query.get(file_id)
        if file:
            file.reference_count += 1
            db.session.commit()
        
        return {
            'success': True,
            'ownership_id': ownership.id
        }
    
    def get_ownership_stats(self, user_id):
        """
        Get ownership statistics for a user
        
        Args:
            user_id: User ID
        
        Returns:
            dict with statistics
        """
        ownerships = Ownership.query.filter_by(user_id=user_id).all()
        
        total_files = len(ownerships)
        uploaded = len([o for o in ownerships if o.verification_method == 'upload'])
        shared = len([o for o in ownerships if o.verification_method == 'shared'])
        verified_pow = len([o for o in ownerships if o.verification_method == 'pow'])
        
        # Calculate total storage used
        file_ids = [o.file_id for o in ownerships]
        files = File.query.filter(File.id.in_(file_ids)).all()
        total_size = sum([f.file_size for f in files])
        
        return {
            'total_files': total_files,
            'uploaded_files': uploaded,
            'shared_files': shared,
            'pow_verified_files': verified_pow,
            'total_storage_bytes': total_size,
            'total_storage_mb': total_size / (1024 * 1024)
        }
