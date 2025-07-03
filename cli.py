#!/usr/bin/env python3
"""
Command Line Interface for PDF Downloader
"""

import argparse
import sys
import json
from typing import List, Dict

from src.pdf_downloader import PDFDownloader
from config import Config


def main():
    parser = argparse.ArgumentParser(
        description='PDF Research Downloader - Command Line Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all default fields
  python cli.py --all-fields

  # Download specific field
  python cli.py --field cybersecurity

  # Download custom keywords
  python cli.py --keywords "machine learning security" "blockchain privacy"

  # Download with custom settings
  python cli.py --field english_security --max-pdfs 50 --max-pages 2

  # List available fields
  python cli.py --list-fields
        """
    )

    # Main options
    parser.add_argument('--all-fields', action='store_true',
                       help='Download PDFs for all configured fields')
    parser.add_argument('--field', type=str, nargs='+',
                       help='Specific field(s) to download')
    parser.add_argument('--keywords', type=str, nargs='+',
                       help='Custom keywords to search for')
    parser.add_argument('--list-fields', action='store_true',
                       help='List all available fields and keywords')

    # Configuration options
    parser.add_argument('--max-pdfs', type=int, default=Config.MAX_PDF_PER_KEYWORD,
                       help=f'Maximum PDFs per keyword (default: {Config.MAX_PDF_PER_KEYWORD})')
    parser.add_argument('--max-pages', type=int, default=Config.MAX_PAGES_PER_SEARCH,
                       help=f'Maximum pages per search (default: {Config.MAX_PAGES_PER_SEARCH})')
    parser.add_argument('--headless', action='store_true',
                       help='Run browser in headless mode')
    parser.add_argument('--output-dir', type=str,
                       help='Custom output directory')

    # Output options
    parser.add_argument('--json', action='store_true',
                       help='Output results in JSON format')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    # List fields if requested
    if args.list_fields:
        list_fields()
        return

    # Validate arguments
    if not any([args.all_fields, args.field, args.keywords]):
        parser.error("Please specify --all-fields, --field, or --keywords")

    # Run download
    try:
        results = run_download(args)
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print_results(results, args.verbose)
            
    except KeyboardInterrupt:
        print("\n⚠️ Download interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def list_fields():
    """List all available fields and their keywords"""
    fields = Config.get_fields_keywords()
    
    print("📚 Available Research Fields:")
    print("=" * 50)
    
    for field_name, keywords in fields.items():
        print(f"\n🔍 {field_name.replace('_', ' ').upper()}")
        print(f"   Keywords: {len(keywords)}")
        print("   Sample keywords:")
        for keyword in keywords[:3]:
            print(f"     • {keyword}")
        if len(keywords) > 3:
            print(f"     ... and {len(keywords) - 3} more")


def run_download(args) -> Dict:
    """Run the download process based on arguments"""
    
    # Create custom config if needed
    config = Config()
    if args.headless:
        config.HEADLESS_MODE = True
    if args.output_dir:
        config.BASE_DOWNLOAD_DIR = args.output_dir
    
    # Initialize downloader
    downloader = PDFDownloader(config)
    
    # Prepare fields and keywords
    fields_keywords = {}
    
    if args.all_fields:
        fields_keywords = config.get_fields_keywords()
    elif args.field:
        all_fields = config.get_fields_keywords()
        for field in args.field:
            if field in all_fields:
                fields_keywords[field] = all_fields[field]
            else:
                print(f"⚠️ Warning: Field '{field}' not found, skipping")
    
    # Add custom keywords
    if args.keywords:
        fields_keywords['custom'] = args.keywords
    
    if not fields_keywords:
        raise ValueError("No valid fields or keywords specified")
    
    print("🚀 Starting PDF download process...")
    print(f"📊 Configuration:")
    print(f"   Max PDFs per keyword: {args.max_pdfs}")
    print(f"   Max pages per search: {args.max_pages}")
    print(f"   Headless mode: {args.headless}")
    print(f"   Output directory: {config.get_download_path()}")
    
    # Run download
    results = downloader.download_all_pdfs(fields_keywords)
    
    return results


def print_results(results: Dict, verbose: bool = False):
    """Print download results in a readable format"""
    
    print("\n" + "=" * 60)
    print("📋 DOWNLOAD RESULTS")
    print("=" * 60)
    
    total_downloaded = 0
    total_failed = 0
    total_keywords = 0
    
    for field_name, field_results in results.items():
        print(f"\n📂 Field: {field_name.replace('_', ' ').upper()}")
        print("-" * 40)
        
        field_downloaded = 0
        field_failed = 0
        
        for result in field_results:
            total_keywords += 1
            
            if 'error' in result:
                print(f"❌ {result['keyword']}: {result['error']}")
                field_failed += 1
                total_failed += 1
            else:
                print(f"✅ {result['keyword']}: {result['downloaded_count']} PDFs downloaded")
                field_downloaded += result['downloaded_count']
                total_downloaded += result['downloaded_count']
                
                if verbose:
                    print(f"   📄 Total URLs found: {result['total_urls_found']}")
                    print(f"   ❌ Failed downloads: {result['failed_count']}")
                    print(f"   📁 Save path: {result['save_path']}")
        
        print(f"\n📊 Field Summary: {field_downloaded} PDFs downloaded, {field_failed} keywords failed")
    
    print("\n" + "=" * 60)
    print("🎯 FINAL SUMMARY")
    print("=" * 60)
    print(f"📚 Total keywords processed: {total_keywords}")
    print(f"📄 Total PDFs downloaded: {total_downloaded}")
    print(f"❌ Total failed keywords: {total_failed}")
    print(f"📁 Files saved to: {Config.get_download_path()}")
    
    if total_downloaded > 0:
        print("🎉 Download completed successfully!")
    else:
        print("⚠️ No PDFs were downloaded. Check your keywords and configuration.")


if __name__ == '__main__':
    main() 