import os
import datetime
from pathlib import Path

class DataCollector:
    """
    General-purpose utility for collecting and saving data from various sources
    """
    
    def __init__(self):
        """Initialize with empty tracking lists"""
        self.saved_files = []
        self.current_output_dir = None
    
    def create_date_folder(self, base_dir="output"):
        """Create a folder with today's date as name"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        output_dir = Path(base_dir) / today
        os.makedirs(output_dir, exist_ok=True)
        self.current_output_dir = output_dir
        return output_dir
    
    def save_links_to_file(self, source_id, links, output_dir=None, source_type=None):
        """Save links to a text file"""
        if not links:
            print(f"No links found for ID: {source_id}")
            return None
        
        # Create output directory if needed
        if output_dir is None:
            output_dir = self.create_date_folder()
        
        # Create file name with source type prefix if provided
        prefix = f"{source_type}_" if source_type else ""
        output_file = output_dir / f"{prefix}{source_id}_links.txt"
        
        # Write links to file
        with open(output_file, "w") as f:
            for link in links:
                f.write(f"{source_id}_{link}\n")
        
        print(f"Saved {len(links)} links for ID {source_id} to {output_file}")
        
        # Track the saved file
        self.saved_files.append((source_id, str(output_file), len(links)))
        
        return str(output_file)
    
    def batch_save_links(self, article_dict, source_type=None):
        """Save multiple sets of links to files in a batch operation"""
        output_dir = self.create_date_folder()
        
        for article_id, links in article_dict.items():
            if links:
                self.save_links_to_file(article_id, links, output_dir, source_type)
        
        return str(output_dir) if self.saved_files else None
    
    def print_summary(self):
        """Print a summary of all files created during this run"""
        if not self.saved_files:
            print("\n📌 No files were saved in this run.")
            return
        
        print("\n📝 Summary of Saved Files:")
        print(f"📁 Output Directory: {self.current_output_dir}")
        print(f"📊 Total Files Created: {len(self.saved_files)}")
        
        total_links = sum(count for _, _, count in self.saved_files)
        print(f"🔗 Total Links Saved: {total_links}")
        
        # Optional: Print detailed list of files if not too many
        if len(self.saved_files) <= 10:  # Only show details if 10 or fewer files
            print("\nDetailed File List:")
            for source_id, file_path, link_count in self.saved_files:
                print(f"  • {source_id}: {link_count} links - {file_path}")
        
        print(f"\n✅ All data has been successfully saved to: {self.current_output_dir}")
