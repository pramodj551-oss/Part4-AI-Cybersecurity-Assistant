#!/usr/bin/env python3
# =============================================================================
# Repository Synchronization Script
# Automates data and model synchronization across all 4 cybersecurity repos
# Version: 1.0
# =============================================================================

from __future__ import annotations

import os
import shutil
import subprocess
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import hashlib


# =============================================================================
# Logging Configuration
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sync_repos.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# =============================================================================
# Repository Synchronizer Class
# =============================================================================

class RepositorySynchronizer:
    """Synchronizes data and models across multiple repositories."""
    
    def __init__(
        self,
        part4_path: str = '.',
        part1_path: str = '../Part1-Cybersecurity-Data-Pipeline',
        part2_path: str = '../Part2-Cybersecurity-ML-Pipeline',
        part3_path: str = '../Part3-Cybersecurity-Dashboard'
    ):
        """Initialize the synchronizer with repository paths."""
        self.part4_path = Path(part4_path).resolve()
        self.part1_path = Path(part1_path).resolve()
        self.part2_path = Path(part2_path).resolve()
        self.part3_path = Path(part3_path).resolve()
        
        self.sync_log = {
            'timestamp': datetime.now().isoformat(),
            'synced_files': [],
            'errors': [],
            'checksums': {}
        }
        
        logger.info("=" * 80)
        logger.info("Repository Synchronizer Initialized")
        logger.info(f"Part 4 (RAG Assistant): {self.part4_path}")
        logger.info(f"Part 1 (Data Pipeline): {self.part1_path}")
        logger.info(f"Part 2 (ML Pipeline): {self.part2_path}")
        logger.info(f"Part 3 (Dashboard): {self.part3_path}")
        logger.info("=" * 80)
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _ensure_directory(self, dir_path: Path) -> None:
        """Ensure directory exists."""
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Directory ensured: {dir_path}")
    
    def _copy_file(
        self,
        src: Path,
        dst: Path,
        check_source: bool = True
    ) -> bool:
        """Copy file with validation and checksum tracking."""
        try:
            if check_source and not src.exists():
                logger.warning(f"Source file not found: {src}")
                self.sync_log['errors'].append(f"Source not found: {src}")
                return False
            
            self._ensure_directory(dst.parent)
            
            # Calculate source checksum before copy
            src_checksum = self._calculate_checksum(src)
            
            # Copy file
            shutil.copy2(src, dst)
            
            # Verify copy
            dst_checksum = self._calculate_checksum(dst)
            
            if src_checksum == dst_checksum:
                logger.info(f"✓ Copied: {src.name} → {dst.relative_to(self.part4_path)}")
                self.sync_log['synced_files'].append({
                    'source': str(src),
                    'destination': str(dst),
                    'checksum': src_checksum,
                    'timestamp': datetime.now().isoformat()
                })
                self.sync_log['checksums'][str(dst)] = src_checksum
                return True
            else:
                error_msg = f"Checksum mismatch for {src.name}"
                logger.error(error_msg)
                self.sync_log['errors'].append(error_msg)
                return False
        
        except Exception as e:
            error_msg = f"Error copying {src.name}: {str(e)}"
            logger.error(error_msg)
            self.sync_log['errors'].append(error_msg)
            return False
    
    def _copy_directory(
        self,
        src: Path,
        dst: Path,
        check_source: bool = True
    ) -> bool:
        """Copy directory recursively with validation."""
        try:
            if check_source and not src.exists():
                logger.warning(f"Source directory not found: {src}")
                self.sync_log['errors'].append(f"Directory not found: {src}")
                return False
            
            self._ensure_directory(dst)
            
            logger.info(f"Copying directory: {src.name} → {dst.relative_to(self.part4_path)}")
            shutil.copytree(src, dst, dirs_exist_ok=True)
            
            logger.info(f"✓ Directory synced: {src.name}")
            return True
        
        except Exception as e:
            error_msg = f"Error copying directory {src.name}: {str(e)}"
            logger.error(error_msg)
            self.sync_log['errors'].append(error_msg)
            return False
    
    # =========================================================================
    # Part 1: Data Pipeline Synchronization
    # =========================================================================
    
    def sync_part1_data(self) -> bool:
        """Synchronize data from Part 1 (Data Pipeline)."""
        logger.info("\n" + "=" * 80)
        logger.info("SYNCING PART 1: Data Pipeline")
        logger.info("=" * 80)
        
        success = True
        
        # Files to sync from Part 1
        files_to_sync = {
            'cybersecurity_incidents.csv': 'data/cybersecurity_incidents.csv',
            'kpi_metrics.json': 'data/kpi_metrics.json',
            'security_events.csv': 'data/security_events.csv',
            'alerts.json': 'data/alerts.json',
        }
        
        # Copy individual files
        for src_file, rel_path in files_to_sync.items():
            src = self.part1_path / 'data' / src_file
            dst = self.part4_path / rel_path
            
            if not self._copy_file(src, dst, check_source=True):
                success = False
        
        # Directories to sync from Part 1
        dirs_to_sync = {
            'sop_documents': 'data/sop_documents',
            'knowledge_base': 'data/knowledge_base',
        }
        
        for src_dir, rel_path in dirs_to_sync.items():
            src = self.part1_path / 'data' / src_dir
            dst = self.part4_path / rel_path
            
            if src.exists():
                if not self._copy_directory(src, dst, check_source=True):
                    success = False
            else:
                logger.warning(f"Optional directory not found: {src}")
        
        logger.info("Part 1 synchronization completed")
        return success
    
    # =========================================================================
    # Part 2: ML Pipeline Synchronization
    # =========================================================================
    
    def sync_part2_models(self) -> bool:
        """Synchronize models and artifacts from Part 2 (ML Pipeline)."""
        logger.info("\n" + "=" * 80)
        logger.info("SYNCING PART 2: ML Pipeline")
        logger.info("=" * 80)
        
        success = True
        
        # Models to sync from Part 2
        models_to_sync = {
            'trained_model.pkl': 'models/trained_model.pkl',
            'feature_scaler.pkl': 'models/feature_scaler.pkl',
            'label_encoder.pkl': 'models/label_encoder.pkl',
            'preprocessing_pipeline.pkl': 'models/preprocessing_pipeline.pkl',
        }
        
        # Copy model files
        for src_file, rel_path in models_to_sync.items():
            src = self.part2_path / 'models' / src_file
            dst = self.part4_path / rel_path
            
            if not self._copy_file(src, dst, check_source=True):
                success = False
        
        # Metadata files from Part 2
        metadata_files = {
            'feature_names.json': 'models/feature_names.json',
            'model_metrics.json': 'models/model_metrics.json',
            'class_labels.json': 'models/class_labels.json',
            'hyperparameters.json': 'models/hyperparameters.json',
        }
        
        for src_file, rel_path in metadata_files.items():
            src = self.part2_path / 'models' / src_file
            dst = self.part4_path / rel_path
            
            if not self._copy_file(src, dst, check_source=True):
                success = False
        
        # Predictions data from Part 2
        predictions_src = self.part2_path / 'data' / 'predictions.csv'
        predictions_dst = self.part4_path / 'data' / 'predictions.csv'
        
        if not self._copy_file(predictions_src, predictions_dst, check_source=True):
            success = False
        
        logger.info("Part 2 synchronization completed")
        return success
    
    # =========================================================================
    # Part 3: Dashboard Synchronization
    # =========================================================================
    
    def sync_part3_config(self) -> bool:
        """Synchronize configuration from Part 3 (Dashboard)."""
        logger.info("\n" + "=" * 80)
        logger.info("SYNCING PART 3: Dashboard Configuration")
        logger.info("=" * 80)
        
        success = True
        
        # Config files to sync
        config_files = {
            'config.py': 'config/config_part3.py',
            'theme.json': 'config/theme.json',
        }
        
        for src_file, rel_path in config_files.items():
            src = self.part3_path / 'config' / src_file
            dst = self.part4_path / rel_path
            
            if not self._copy_file(src, dst, check_source=True):
                success = False
        
        logger.info("Part 3 synchronization completed")
        return success
    
    # =========================================================================
    # Vector Store Rebuilding
    # =========================================================================
    
    def rebuild_vector_indices(self) -> bool:
        """Rebuild FAISS vector indices after data sync."""
        logger.info("\n" + "=" * 80)
        logger.info("REBUILDING VECTOR INDICES")
        logger.info("=" * 80)
        
        try:
            vectorstore_script = self.part4_path / 'src' / 'vector_store.py'
            
            if not vectorstore_script.exists():
                logger.warning(f"Vector store script not found: {vectorstore_script}")
                return False
            
            logger.info("Running vector store rebuild...")
            result = subprocess.run(
                ['python', str(vectorstore_script), '--rebuild'],
                cwd=self.part4_path,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            if result.returncode == 0:
                logger.info("✓ Vector indices rebuilt successfully")
                return True
            else:
                error_msg = f"Vector index rebuild failed: {result.stderr}"
                logger.error(error_msg)
                self.sync_log['errors'].append(error_msg)
                return False
        
        except subprocess.TimeoutExpired:
            error_msg = "Vector index rebuild timed out"
            logger.error(error_msg)
            self.sync_log['errors'].append(error_msg)
            return False
        
        except Exception as e:
            error_msg = f"Error rebuilding vector indices: {str(e)}"
            logger.error(error_msg)
            self.sync_log['errors'].append(error_msg)
            return False
    
    # =========================================================================
    # Validation
    # =========================================================================
    
    def validate_sync(self) -> bool:
        """Validate synchronized data integrity."""
        logger.info("\n" + "=" * 80)
        logger.info("VALIDATING SYNCHRONIZATION")
        logger.info("=" * 80)
        
        validation_passed = True
        
        # Check critical files
        critical_files = [
            'data/cybersecurity_incidents.csv',
            'data/kpi_metrics.json',
            'models/trained_model.pkl',
            'data/predictions.csv',
        ]
        
        for file_path in critical_files:
            full_path = self.part4_path / file_path
            if full_path.exists():
                file_size = full_path.stat().st_size
                logger.info(f"✓ Found: {file_path} ({file_size} bytes)")
            else:
                logger.warning(f"✗ Missing: {file_path}")
                validation_passed = False
        
        # Check critical directories
        critical_dirs = [
            'data/sop_documents',
            'data/knowledge_base',
            'vectorstore',
        ]
        
        for dir_path in critical_dirs:
            full_path = self.part4_path / dir_path
            if full_path.exists():
                file_count = len(list(full_path.glob('**/*')))
                logger.info(f"✓ Found: {dir_path} ({file_count} items)")
            else:
                logger.warning(f"✗ Missing: {dir_path}")
                # Note: vectorstore is optional on first run
                if dir_path != 'vectorstore':
                    validation_passed = False
        
        return validation_passed
    
    # =========================================================================
    # Main Synchronization
    # =========================================================================
    
    def sync_all(self, skip_rebuild: bool = False) -> bool:
        """Run complete synchronization."""
        logger.info("\n" + "=" * 80)
        logger.info("STARTING COMPLETE SYNCHRONIZATION")
        logger.info("=" * 80)
        
        results = {
            'part1_data': False,
            'part2_models': False,
            'part3_config': False,
            'vector_indices': False,
            'validation': False,
        }
        
        # Step 1: Sync Part 1 Data
        try:
            results['part1_data'] = self.sync_part1_data()
        except Exception as e:
            logger.error(f"Part 1 sync failed: {str(e)}")
            self.sync_log['errors'].append(f"Part 1 sync: {str(e)}")
        
        # Step 2: Sync Part 2 Models
        try:
            results['part2_models'] = self.sync_part2_models()
        except Exception as e:
            logger.error(f"Part 2 sync failed: {str(e)}")
            self.sync_log['errors'].append(f"Part 2 sync: {str(e)}")
        
        # Step 3: Sync Part 3 Config
        try:
            results['part3_config'] = self.sync_part3_config()
        except Exception as e:
            logger.error(f"Part 3 sync failed: {str(e)}")
            self.sync_log['errors'].append(f"Part 3 sync: {str(e)}")
        
        # Step 4: Rebuild Vector Indices
        if not skip_rebuild:
            try:
                results['vector_indices'] = self.rebuild_vector_indices()
            except Exception as e:
                logger.error(f"Vector index rebuild failed: {str(e)}")
                self.sync_log['errors'].append(f"Vector index: {str(e)}")
        else:
            logger.info("Skipping vector index rebuild (--skip-rebuild flag)")
            results['vector_indices'] = True
        
        # Step 5: Validate
        try:
            results['validation'] = self.validate_sync()
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            self.sync_log['errors'].append(f"Validation: {str(e)}")
        
        # Save sync log
        self._save_sync_log(results)
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("SYNCHRONIZATION SUMMARY")
        logger.info("=" * 80)
        
        for step, passed in results.items():
            status = "✓ PASSED" if passed else "✗ FAILED"
            logger.info(f"{step:.<50} {status}")
        
        overall_success = all(results.values())
        logger.info("=" * 80)
        logger.info(f"Overall Status: {'✓ SUCCESS' if overall_success else '✗ FAILED'}")
        logger.info("=" * 80)
        
        return overall_success
    
    def _save_sync_log(self, results: Dict[str, bool]) -> None:
        """Save synchronization log to JSON file."""
        self.sync_log['results'] = results
        self.sync_log['overall_success'] = all(results.values())
        
        log_file = self.part4_path / 'sync_log.json'
        
        try:
            with open(log_file, 'w') as f:
                json.dump(self.sync_log, f, indent=2)
            logger.info(f"Sync log saved: {log_file}")
        except Exception as e:
            logger.error(f"Failed to save sync log: {str(e)}")


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """Command-line interface for the synchronizer."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Synchronize data and models across cybersecurity repositories'
    )
    
    parser.add_argument(
        '--part4-path',
        default='.',
        help='Path to Part 4 (RAG Assistant) repository'
    )
    
    parser.add_argument(
        '--part1-path',
        default='../Part1-Cybersecurity-Data-Pipeline',
        help='Path to Part 1 (Data Pipeline) repository'
    )
    
    parser.add_argument(
        '--part2-path',
        default='../Part2-Cybersecurity-ML-Pipeline',
        help='Path to Part 2 (ML Pipeline) repository'
    )
    
    parser.add_argument(
        '--part3-path',
        default='../Part3-Cybersecurity-Dashboard',
        help='Path to Part 3 (Dashboard) repository'
    )
    
    parser.add_argument(
        '--skip-rebuild',
        action='store_true',
        help='Skip vector index rebuild'
    )
    
    parser.add_argument(
        '--part1-only',
        action='store_true',
        help='Sync only Part 1 data'
    )
    
    parser.add_argument(
        '--part2-only',
        action='store_true',
        help='Sync only Part 2 models'
    )
    
    parser.add_argument(
        '--part3-only',
        action='store_true',
        help='Sync only Part 3 config'
    )
    
    args = parser.parse_args()
    
    # Initialize synchronizer
    syncer = RepositorySynchronizer(
        part4_path=args.part4_path,
        part1_path=args.part1_path,
        part2_path=args.part2_path,
        part3_path=args.part3_path
    )
    
    # Execute synchronization
    if args.part1_only:
        success = syncer.sync_part1_data()
    elif args.part2_only:
        success = syncer.sync_part2_models()
    elif args.part3_only:
        success = syncer.sync_part3_config()
    else:
        success = syncer.sync_all(skip_rebuild=args.skip_rebuild)
    
    # Exit with appropriate code
    exit(0 if success else 1)


if __name__ == '__main__':
    main()
