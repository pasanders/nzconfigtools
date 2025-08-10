"""
Batch Menu Manager for Nikon Z Cameras
Manage multiple camera configurations and batch operations
"""

import sys
import os
import json
import time
from pathlib import Path
import argparse
from datetime import datetime

class BatchMenuManager:
    def __init__(self):
        self.config_dir = Path.home() / ".nikon_z_configs"
        self.config_dir.mkdir(exist_ok=True)
        
        self.profiles_file = self.config_dir / "profiles.json"
        self.load_profiles()
    
    def load_profiles(self):
        """Load saved configuration profiles"""
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r') as f:
                    self.profiles = json.load(f)
            except:
                self.profiles = {}
        else:
            self.profiles = {}
    
    def save_profiles(self):
        """Save configuration profiles"""
        with open(self.profiles_file, 'w') as f:
            json.dump(self.profiles, f, indent=2)
    
    def create_profile(self, name, description, source_file):
        """Create a new configuration profile"""
        source_path = Path(source_file)
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_file}")
        
        # Create profile directory
        profile_dir = self.config_dir / "profiles" / name
        profile_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy file to profile directory
        profile_file = profile_dir / "config.bin"
        with open(source_path, 'rb') as src, open(profile_file, 'wb') as dst:
            dst.write(src.read())
        
        # Extract metadata from file
        metadata = self.extract_file_metadata(source_path)
        
        # Save profile info
        self.profiles[name] = {
            'description': description,
            'created': datetime.now().isoformat(),
            'file_path': str(profile_file),
            'file_size': source_path.stat().st_size,
            'camera_model': metadata.get('camera_model', 'Unknown'),
            'firmware': metadata.get('firmware', 'Unknown'),
            'last_used': None
        }
        
        self.save_profiles()
        print(f"✓ Profile '{name}' created successfully")
    
    def extract_file_metadata(self, file_path):
        """Extract metadata from a camera configuration file"""
        metadata = {}
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Extract camera model
            if len(data) > 10:
                model_bytes = data[0:11]
                null_pos = model_bytes.find(0)
                if null_pos >= 0:
                    model_bytes = model_bytes[:null_pos]
                try:
                    metadata['camera_model'] = model_bytes.decode('ascii')
                except UnicodeDecodeError:
                    metadata['camera_model'] = 'Unknown'
            
            # Extract firmware version
            if len(data) > 28:
                fw_bytes = data[24:29]
                null_pos = fw_bytes.find(0)
                if null_pos >= 0:
                    fw_bytes = fw_bytes[:null_pos]
                try:
                    metadata['firmware'] = fw_bytes.decode('ascii')
                except UnicodeDecodeError:
                    metadata['firmware'] = 'Unknown'
        
        except Exception:
            pass
        
        return metadata
    
    def list_profiles(self):
        """List all saved profiles"""
        if not self.profiles:
            print("No profiles found. Create a profile with 'create' command.")
            return
        
        print("Saved Configuration Profiles:")
        print("=" * 60)
        
        for name, profile in self.profiles.items():
            print(f"\nProfile: {name}")
            print(f"  Description: {profile['description']}")
            print(f"  Camera: {profile['camera_model']}")
            print(f"  Firmware: {profile['firmware']}")
            print(f"  Created: {profile['created'][:19].replace('T', ' ')}")
            if profile['last_used']:
                print(f"  Last Used: {profile['last_used'][:19].replace('T', ' ')}")
            print(f"  File Size: {profile['file_size']} bytes")
            
            # Check if file still exists
            if not Path(profile['file_path']).exists():
                print("  ⚠ Warning: Profile file missing!")
    
    def apply_profile(self, profile_name, target_drive=None):
        """Apply a profile to camera"""
        if profile_name not in self.profiles:
            raise ValueError(f"Profile '{profile_name}' not found")
        
        profile = self.profiles[profile_name]
        profile_file = Path(profile['file_path'])
        
        if not profile_file.exists():
            raise FileNotFoundError(f"Profile file missing: {profile_file}")
        
        # Use camera uploader to upload the file
        from camera_uploader import CameraUploader
        
        uploader = CameraUploader()
        uploader.upload_menu_file(
            str(profile_file),
            target_drive=target_drive,
            backup_existing=True
        )
        
        # Update last used timestamp
        self.profiles[profile_name]['last_used'] = datetime.now().isoformat()
        self.save_profiles()
        
        print(f"✓ Profile '{profile_name}' applied successfully")
    
    def delete_profile(self, profile_name):
        """Delete a configuration profile"""
        if profile_name not in self.profiles:
            raise ValueError(f"Profile '{profile_name}' not found")
        
        profile = self.profiles[profile_name]
        
        # Confirm deletion
        response = input(f"Delete profile '{profile_name}'? This cannot be undone. (y/N): ")
        if response.lower() != 'y':
            print("Deletion cancelled")
            return
        
        # Delete profile file
        profile_file = Path(profile['file_path'])
        if profile_file.exists():
            profile_file.unlink()
        
        # Remove from profiles
        del self.profiles[profile_name]
        self.save_profiles()
        
        print(f"✓ Profile '{profile_name}' deleted")
    
    def backup_current_config(self, name=None, description=None):
        """Backup current camera configuration"""
        from camera_uploader import CameraUploader
        
        uploader = CameraUploader()
        
        # Generate filename if not provided
        if name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"backup_{timestamp}"
        
        if description is None:
            description = f"Automatic backup created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Download current config
        temp_file = self.config_dir / f"temp_{name}.bin"
        try:
            uploader.download_menu_file(target_file=str(temp_file))
            
            # Create profile from downloaded config
            self.create_profile(name, description, str(temp_file))
            
            # Clean up temp file
            temp_file.unlink()
            
            print(f"✓ Current camera configuration backed up as profile '{name}'")
            
        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            raise e
    
    def compare_profiles(self, profile1, profile2):
        """Compare two configuration profiles"""
        if profile1 not in self.profiles:
            raise ValueError(f"Profile '{profile1}' not found")
        if profile2 not in self.profiles:
            raise ValueError(f"Profile '{profile2}' not found")
        
        file1 = Path(self.profiles[profile1]['file_path'])
        file2 = Path(self.profiles[profile2]['file_path'])
        
        if not file1.exists():
            raise FileNotFoundError(f"Profile file missing: {file1}")
        if not file2.exists():
            raise FileNotFoundError(f"Profile file missing: {file2}")
        
        print(f"Comparing profiles: '{profile1}' vs '{profile2}'")
        print("=" * 60)
        
        # Basic comparison
        size1 = file1.stat().st_size
        size2 = file2.stat().st_size
        
        print(f"File sizes: {size1} vs {size2} bytes")
        
        if size1 != size2:
            print("⚠ Files have different sizes - likely different camera models or formats")
            return
        
        # Content comparison
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            data1 = f1.read()
            data2 = f2.read()
        
        if data1 == data2:
            print("✓ Files are identical")
            return
        
        # Find differences
        differences = []
        for i, (byte1, byte2) in enumerate(zip(data1, data2)):
            if byte1 != byte2:
                differences.append((i, byte1, byte2))
        
        print(f"Found {len(differences)} byte differences")
        
        if len(differences) <= 20:  # Show details for small differences
            print("\nByte-level differences:")
            for offset, byte1, byte2 in differences[:20]:
                print(f"  Offset {offset:06x}: {byte1:02x} → {byte2:02x}")
        else:
            print(f"\nFirst 10 differences:")
            for offset, byte1, byte2 in differences[:10]:
                print(f"  Offset {offset:06x}: {byte1:02x} → {byte2:02x}")
            print(f"  ... and {len(differences) - 10} more")
    
    def export_profile(self, profile_name, output_file):
        """Export a profile to a standalone file"""
        if profile_name not in self.profiles:
            raise ValueError(f"Profile '{profile_name}' not found")
        
        profile = self.profiles[profile_name]
        profile_file = Path(profile['file_path'])
        
        if not profile_file.exists():
            raise FileNotFoundError(f"Profile file missing: {profile_file}")
        
        output_path = Path(output_file)
        
        # Copy file
        with open(profile_file, 'rb') as src, open(output_path, 'wb') as dst:
            dst.write(src.read())
        
        print(f"✓ Profile '{profile_name}' exported to: {output_file}")
    
    def import_profile(self, name, description, source_file):
        """Import a profile from an external file"""
        # This is essentially the same as create_profile
        self.create_profile(name, description, source_file)

def main():
    parser = argparse.ArgumentParser(description="Batch Menu Manager for Nikon Z Cameras")
    parser.add_argument("--version", action="version", version="1.0")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create profile
    create_parser = subparsers.add_parser("create", help="Create a new configuration profile")
    create_parser.add_argument("name", help="Profile name")
    create_parser.add_argument("file", help="Source configuration file")
    create_parser.add_argument("--description", help="Profile description")
    
    # List profiles
    list_parser = subparsers.add_parser("list", help="List all saved profiles")
    
    # Apply profile
    apply_parser = subparsers.add_parser("apply", help="Apply a profile to camera")
    apply_parser.add_argument("name", help="Profile name to apply")
    apply_parser.add_argument("--drive", help="Target camera drive")
    
    # Delete profile
    delete_parser = subparsers.add_parser("delete", help="Delete a configuration profile")
    delete_parser.add_argument("name", help="Profile name to delete")
    
    # Backup current
    backup_parser = subparsers.add_parser("backup", help="Backup current camera configuration")
    backup_parser.add_argument("--name", help="Backup name (auto-generated if not specified)")
    backup_parser.add_argument("--description", help="Backup description")
    
    # Compare profiles
    compare_parser = subparsers.add_parser("compare", help="Compare two configuration profiles")
    compare_parser.add_argument("profile1", help="First profile to compare")
    compare_parser.add_argument("profile2", help="Second profile to compare")
    
    # Export profile
    export_parser = subparsers.add_parser("export", help="Export a profile to a file")
    export_parser.add_argument("name", help="Profile name to export")
    export_parser.add_argument("output", help="Output file path")
    
    # Import profile
    import_parser = subparsers.add_parser("import", help="Import a profile from a file")
    import_parser.add_argument("name", help="Profile name")
    import_parser.add_argument("file", help="Source file to import")
    import_parser.add_argument("--description", help="Profile description")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = BatchMenuManager()
    
    try:
        if args.command == "create":
            description = args.description or f"Profile created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            manager.create_profile(args.name, description, args.file)
            
        elif args.command == "list":
            manager.list_profiles()
            
        elif args.command == "apply":
            manager.apply_profile(args.name, target_drive=args.drive)
            
        elif args.command == "delete":
            manager.delete_profile(args.name)
            
        elif args.command == "backup":
            manager.backup_current_config(name=args.name, description=args.description)
            
        elif args.command == "compare":
            manager.compare_profiles(args.profile1, args.profile2)
            
        elif args.command == "export":
            manager.export_profile(args.name, args.output)
            
        elif args.command == "import":
            description = args.description or f"Imported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            manager.import_profile(args.name, description, args.file)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
