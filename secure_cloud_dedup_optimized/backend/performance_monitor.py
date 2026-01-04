"""
Performance monitoring module
Tracks and analyzes system performance metrics
"""
import time
from datetime import datetime, timedelta
from .models import db, PerformanceMetric
import json


class PerformanceMonitor:
    """Performance monitoring and analytics"""
    
    def __init__(self):
        """Initialize performance monitor"""
        self.current_metrics = {}
    
    def record_metric(self, metric_type, value, unit='', metadata=None):
        """
        Record a performance metric
        
        Args:
            metric_type: Type of metric (upload, dedup, encryption, etc.)
            value: Metric value
            unit: Unit of measurement
            metadata: Optional additional data (dict)
        
        Returns:
            PerformanceMetric record
        """
        metric = PerformanceMetric(
            metric_type=metric_type,
            metric_value=value,
            metric_unit=unit,
            metadata=json.dumps(metadata) if metadata else None
        )
        
        db.session.add(metric)
        db.session.commit()
        
        return metric
    
    def get_metrics(self, metric_type=None, hours=24):
        """
        Get performance metrics
        
        Args:
            metric_type: Optional filter by metric type
            hours: Number of hours to look back
        
        Returns:
            List of metrics
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        query = PerformanceMetric.query.filter(
            PerformanceMetric.recorded_at >= cutoff_time
        )
        
        if metric_type:
            query = query.filter_by(metric_type=metric_type)
        
        return query.order_by(PerformanceMetric.recorded_at.desc()).all()
    
    def get_average_metric(self, metric_type, hours=24):
        """
        Get average value for a metric type
        
        Args:
            metric_type: Type of metric
            hours: Number of hours to look back
        
        Returns:
            Average value
        """
        metrics = self.get_metrics(metric_type, hours)
        
        if not metrics:
            return 0
        
        total = sum([m.metric_value for m in metrics])
        return total / len(metrics)
    
    def get_upload_stats(self, hours=24):
        """Get upload performance statistics"""
        from .models import Upload
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        uploads = Upload.query.filter(
            Upload.upload_date >= cutoff_time
        ).all()
        
        if not uploads:
            return {
                'total_uploads': 0,
                'average_time_ms': 0,
                'duplicates': 0,
                'unique_files': 0
            }
        
        total_time = sum([u.upload_time_ms for u in uploads if u.upload_time_ms])
        duplicates = len([u for u in uploads if u.was_duplicate])
        
        return {
            'total_uploads': len(uploads),
            'average_time_ms': total_time / len(uploads) if uploads else 0,
            'duplicates': duplicates,
            'unique_files': len(uploads) - duplicates,
            'dedup_rate': (duplicates / len(uploads)) * 100 if uploads else 0
        }
    
    def get_encryption_stats(self, hours=24):
        """Get encryption performance statistics"""
        metrics = self.get_metrics('encryption', hours)
        
        if not metrics:
            return {
                'total_encryptions': 0,
                'average_time': 0,
                'optimized_count': 0,
                'traditional_count': 0
            }
        
        optimized = []
        traditional = []
        
        for metric in metrics:
            if metric.metadata:
                meta = json.loads(metric.metadata)
                if meta.get('method') == 'optimized_convergent':
                    optimized.append(metric.metric_value)
                else:
                    traditional.append(metric.metric_value)
        
        return {
            'total_encryptions': len(metrics),
            'average_time': sum([m.metric_value for m in metrics]) / len(metrics),
            'optimized_count': len(optimized),
            'traditional_count': len(traditional),
            'optimized_avg_time': sum(optimized) / len(optimized) if optimized else 0,
            'traditional_avg_time': sum(traditional) / len(traditional) if traditional else 0,
            'speedup': (sum(traditional) / len(traditional)) / (sum(optimized) / len(optimized)) if optimized and traditional else 1
        }
    
    def get_dedup_stats(self, hours=24):
        """Get deduplication statistics"""
        metrics = self.get_metrics('deduplication', hours)
        
        return {
            'total_dedup_checks': len(metrics),
            'duplicates_found': len([m for m in metrics if m.metric_value == 1.0])
        }
    
    def get_system_overview(self):
        """Get comprehensive system overview"""
        from .models import File, Upload, User, Block
        
        # Overall stats
        total_users = User.query.count()
        total_files = File.query.count()
        total_uploads = Upload.query.count()
        total_blocks = Block.query.count()
        
        # Storage stats
        total_storage = db.session.query(db.func.sum(File.file_size)).scalar() or 0
        
        # Recent performance (last 24 hours)
        upload_stats = self.get_upload_stats(24)
        encryption_stats = self.get_encryption_stats(24)
        
        return {
            'users': total_users,
            'unique_files': total_files,
            'total_uploads': total_uploads,
            'total_blocks': total_blocks,
            'total_storage_mb': total_storage / (1024 * 1024),
            'recent_uploads': upload_stats,
            'recent_encryption': encryption_stats,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_realtime_metrics(self):
        """Get real-time metrics for dashboard"""
        # Get metrics from last 5 minutes
        recent_metrics = self.get_metrics(hours=0.083)  # 5 minutes
        
        metrics_by_type = {}
        for metric in recent_metrics:
            if metric.metric_type not in metrics_by_type:
                metrics_by_type[metric.metric_type] = []
            metrics_by_type[metric.metric_type].append({
                'value': metric.metric_value,
                'unit': metric.metric_unit,
                'timestamp': metric.recorded_at.isoformat()
            })
        
        return metrics_by_type
    
    def generate_performance_report(self, hours=24):
        """
        Generate comprehensive performance report
        
        Args:
            hours: Number of hours to analyze
        
        Returns:
            dict with detailed performance report
        """
        report = {
            'report_period_hours': hours,
            'generated_at': datetime.utcnow().isoformat(),
            'system_overview': self.get_system_overview(),
            'upload_performance': self.get_upload_stats(hours),
            'encryption_performance': self.get_encryption_stats(hours),
            'deduplication_performance': self.get_dedup_stats(hours)
        }
        
        return report
