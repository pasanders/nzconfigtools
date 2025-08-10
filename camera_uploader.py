"""
Nikon Z Camera Menu Upload Tool
Automatically uploads menu settings files to camera memory card
Supports multiple camera connection methods and safety checks
"""

import sys
import os
import shutil
import time
import argparse
from pathlib import Path
import platform

class CameraUploader:
    def __init__(self):
        self.system = platform.system().lower()
        self.camera_paths = []
        self.safety_checks = True
        
    def find_camera_drives(self):
        """Find connected camera memory cards"""
        self.camera_paths = []
        
        if self.system == "windows":
            self._find_windows_drives()
        elif self.system == "darwin":  # macOS
            self._find_macos_drives()
        elif self.system == "linux":
            self._find_linux_drives()
        
        return self.camera_paths
    
    def _find_windows_drives(self):
        """Find camera drives on Windows"""
        # Use alternative method that doesn't require win32api
        import string
        
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                if self._is_camera_drive(drive):
                    self.camera_paths.append(drive)
    
    def _find_macos_drives(self):
        """Find camera drives on macOS"""
        volumes_path = Path("/Volumes")
        if volumes_path.exists():
            for volume in volumes_path.iterdir():
                if volume.is_dir() and self._is_camera_drive(str(volume)):
                    self.camera_paths.append(str(volume))
    
    def _find_linux_drives(self):
        """Find camera drives on Linux"""
        # Check common mount points
        mount_points = ["/media", "/mnt", "/run/media"]
        
        for mount_base in mount_points:
            mount_path = Path(mount_base)
            if mount_path.exists():
                # Check user-specific mounts (like /media/username/)
                for user_dir in mount_path.iterdir():
                    if user_dir.is_dir():
                        for volume in user_dir.iterdir():
                            if volume.is_dir() and self._is_camera_drive(str(volume)):
                                self.camera_paths.append(str(volume))
                
                # Also check direct mounts
                for volume in mount_path.iterdir():
                    if volume.is_dir() and self._is_camera_drive(str(volume)):
                        self.camera_paths.append(str(volume))
    
    def _is_camera_drive(self, path):
        """Check if a drive/path is a camera memory card"""
        try:
            drive_path = Path(path)
            
            # Check for camera-specific indicators
            indicators = [
                "DCIM",          # Digital Camera Images folder
                "MISC",          # Misc folder often present on camera cards
                "PRIVATE",       # Private folder on some cameras
                "NIKON",         # Nikon-specific folder
            ]
            
            for indicator in indicators:
                if (drive_path / indicator).exists():
                    return True
            
            # Check for existing camera menu files (different cameras use different names)
            menu_patterns = ["NCSET*.BIN"]
            for pattern in menu_patterns:
                if list(drive_path.glob(pattern)):
                    return True
            
            # Check for typical camera file patterns
            dcim_path = drive_path / "DCIM"
            if dcim_path.exists():
                for folder in dcim_path.iterdir():
                    if folder.is_dir() and any(folder.glob("DSC_*.JPG")):
                        return True
            
            return False
            
        except (OSError, PermissionError):
            return False
    
    def _find_menu_file(self, drive_path):
        """Find the menu file on a camera drive (different cameras use different names)"""
        drive_path = Path(drive_path)
        
        # Common menu file patterns for different Nikon Z cameras
        menu_patterns = [
            "NCSET016.BIN",  # Z5 Mark 2
            "NCSET006.BIN",  # Z5 Mark 1
            "NCSET*.BIN",    # Any NCSET file
        ]
        
        for pattern in menu_patterns:
            if "*" in pattern:
                # Use glob for wildcard patterns
                menu_files = list(drive_path.glob(pattern))
                if menu_files:
                    return menu_files[0]  # Return first match
            else:
                # Direct file check
                menu_file = drive_path / pattern
                if menu_file.exists():
                    return menu_file
        
        return None
    
    def upload_menu_file(self, source_file, target_drive=None, backup_existing=True):
        """Upload menu file to camera"""
        source_path = Path(source_file)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_file}")
        
        # Find camera if not specified
        if target_drive is None:
            cameras = self.find_camera_drives()
            if not cameras:
                raise RuntimeError("No camera memory card detected. Please ensure camera is connected and card is accessible.")
            
            if len(cameras) > 1:
                print("Multiple camera drives detected:")
                for i, drive in enumerate(cameras, 1):
                    print(f"  {i}. {drive}")
                
                while True:
                    try:
                        choice = int(input("Select drive (1-{}): ".format(len(cameras))))
                        if 1 <= choice <= len(cameras):
                            target_drive = cameras[choice - 1]
                            break
                        else:
                            print("Invalid choice. Please try again.")
                    except ValueError:
                        print("Please enter a number.")
            else:
                target_drive = cameras[0]
        
        target_path = Path(target_drive)
        
        # Find existing menu file to determine correct filename
        existing_menu_file = self._find_menu_file(target_path)
        if existing_menu_file:
            target_file = existing_menu_file
            print(f"Found existing menu file: {existing_menu_file.name}")
        else:
            # Default to most common filename if no existing file found
            target_file = target_path / "NCSET006.BIN"
            print("No existing menu file found, using default: NCSET006.BIN")
        
        print(f"Target camera drive: {target_drive}")
        print(f"Source file: {source_file}")
        print(f"Target file: {target_file}")
        
        # Safety checks
        if self.safety_checks:
            self._perform_safety_checks(source_path, target_path)
        
        # Backup existing file if requested
        if backup_existing and target_file.exists():
            backup_name = f"{target_file.stem}_backup_{int(time.time())}{target_file.suffix}"
            backup_file = target_path / backup_name
            print(f"Backing up existing menu file to: {backup_file}")
            shutil.copy2(target_file, backup_file)
        
        # Upload file
        print("Uploading menu file...")
        try:
            shutil.copy2(source_path, target_file)
            print("✓ Upload successful!")
            
            # Verify upload
            if self._verify_upload(source_path, target_file):
                print("✓ Upload verified - files match")
            else:
                print("⚠ Warning: Uploaded file does not match source")
            
        except Exception as e:
            raise RuntimeError(f"Upload failed: {str(e)}")
    
    def _perform_safety_checks(self, source_path, target_path):
        """Perform safety checks before upload"""
        print("Performing safety checks...")
        
        # Check if target is writable
        if not os.access(target_path, os.W_OK):
            raise PermissionError(f"Cannot write to camera drive: {target_path}")
        
        # Check source file size (should be reasonable for a menu file)
        source_size = source_path.stat().st_size
        if source_size < 1000 or source_size > 1000000:  # 1KB to 1MB range
            response = input(f"Warning: Source file size ({source_size} bytes) seems unusual for a menu file. Continue? (y/N): ")
            if response.lower() != 'y':
                raise RuntimeError("Upload cancelled by user")
        
        # Check file format by reading header
        try:
            with open(source_path, 'rb') as f:
                header = f.read(32)
                if not header.startswith(b'NIKON'):
                    response = input("Warning: File does not appear to be a Nikon camera menu file. Continue? (y/N): ")
                    if response.lower() != 'y':
                        raise RuntimeError("Upload cancelled by user")
        except Exception:
            print("Warning: Could not verify file format")
        
        print("✓ Safety checks passed")
    
    def _verify_upload(self, source_path, target_path):
        """Verify that upload was successful"""
        try:
            # Compare file sizes
            source_size = source_path.stat().st_size
            target_size = target_path.stat().st_size
            
            if source_size != target_size:
                return False
            
            # Compare file content (first and last 1KB)
            with open(source_path, 'rb') as src, open(target_path, 'rb') as tgt:
                # Check first 1KB
                src_start = src.read(1024)
                tgt_start = tgt.read(1024)
                
                if src_start != tgt_start:
                    return False
                
                # Check last 1KB
                if source_size > 1024:
                    src.seek(-1024, 2)
                    tgt.seek(-1024, 2)
                    src_end = src.read(1024)
                    tgt_end = tgt.read(1024)
                    
                    if src_end != tgt_end:
                        return False
            
            return True
            
        except Exception:
            return False
    
    def list_camera_drives(self):
        """List all detected camera drives"""
        cameras = self.find_camera_drives()
        
        if not cameras:
            print("No camera memory cards detected.")
            return
        
        print("Detected camera drives:")
        for i, drive in enumerate(cameras, 1):
            drive_path = Path(drive)
            
            # Get drive info
            try:
                total, used, free = shutil.disk_usage(drive)
                total_gb = total / (1024**3)
                free_gb = free / (1024**3)
                
                # Check for existing menu file
                menu_file = self._find_menu_file(drive_path)
                if menu_file:
                    menu_status = f"✓ Has menu file ({menu_file.name})"
                else:
                    menu_status = "✗ No menu file"
                
                print(f"  {i}. {drive}")
                print(f"     Size: {total_gb:.1f} GB (Free: {free_gb:.1f} GB)")
                print(f"     Status: {menu_status}")
                
                # Show some camera indicators
                indicators = []
                if (drive_path / "DCIM").exists():
                    dcim_count = len(list((drive_path / "DCIM").glob("*/*.JPG")))
                    if dcim_count > 0:
                        indicators.append(f"{dcim_count} photos")
                
                if indicators:
                    print(f"     Content: {', '.join(indicators)}")
                
            except OSError:
                print(f"  {i}. {drive} (Cannot access drive info)")
            
            print()
    
    def download_menu_file(self, source_drive=None, target_file=None):
        """Download menu file from camera"""
        # Find camera if not specified
        if source_drive is None:
            cameras = self.find_camera_drives()
            if not cameras:
                raise RuntimeError("No camera memory card detected.")
            
            if len(cameras) > 1:
                print("Multiple camera drives detected:")
                for i, drive in enumerate(cameras, 1):
                    print(f"  {i}. {drive}")
                
                while True:
                    try:
                        choice = int(input("Select drive (1-{}): ".format(len(cameras))))
                        if 1 <= choice <= len(cameras):
                            source_drive = cameras[choice - 1]
                            break
                        else:
                            print("Invalid choice. Please try again.")
                    except ValueError:
                        print("Please enter a number.")
            else:
                source_drive = cameras[0]
        
        source_path_base = Path(source_drive)
        source_path = self._find_menu_file(source_path_base)
        
        if not source_path:
            raise FileNotFoundError(f"No menu file found on camera: {source_drive}")
        
        print(f"Found menu file: {source_path.name}")
        
        # Generate target filename if not specified
        if target_file is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            target_file = f"{source_path.stem}_downloaded_{timestamp}{source_path.suffix}"
        
        target_path = Path(target_file)
        
        print(f"Downloading menu file from: {source_path}")
        print(f"Saving to: {target_path}")
        
        try:
            shutil.copy2(source_path, target_path)
            print("✓ Download successful!")
            
            # Show file info
            file_size = target_path.stat().st_size
            print(f"File size: {file_size} bytes")
            
        except Exception as e:
            raise RuntimeError(f"Download failed: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Nikon Z Camera Menu Upload Tool")
    parser.add_argument("--version", action="version", version="1.0")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload menu file to camera")
    upload_parser.add_argument("file", help="Menu file to upload")
    upload_parser.add_argument("--drive", help="Target camera drive (auto-detect if not specified)")
    upload_parser.add_argument("--no-backup", action="store_true", help="Don't backup existing menu file")
    upload_parser.add_argument("--no-safety-checks", action="store_true", help="Skip safety checks")
    
    # Download command
    download_parser = subparsers.add_parser("download", help="Download menu file from camera")
    download_parser.add_argument("--drive", help="Source camera drive (auto-detect if not specified)")
    download_parser.add_argument("--output", help="Output filename (auto-generate if not specified)")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List detected camera drives")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    uploader = CameraUploader()
    
    try:
        if args.command == "upload":
            uploader.safety_checks = not args.no_safety_checks
            uploader.upload_menu_file(
                args.file,
                target_drive=args.drive,
                backup_existing=not args.no_backup
            )
            
        elif args.command == "download":
            uploader.download_menu_file(
                source_drive=args.drive,
                target_file=args.output
            )
            
        elif args.command == "list":
            uploader.list_camera_drives()
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
