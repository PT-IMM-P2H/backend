"""
Script to parse P2H checklist items from Excel files.

This script reads the P2H forms for EV and LV vehicles and populates
the checklist_templates table in the database.

Files to parse:
- docs/Form P2H Unit EV.xlsx
- docs/P2h Unit LV.xlsx
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.checklist import ChecklistTemplate
from app.models.vehicle import VehicleType


def parse_ev_checklist(file_path: str) -> list[dict]:
    """
    Parse EV checklist from Excel file.
    
    Args:
        file_path: Path to EV Excel file
        
    Returns:
        List of checklist items
    """
    print(f"📖 Reading EV checklist from: {file_path}")
    
    # TODO: Adjust based on actual Excel structure
    # You may need to specify sheet_name, header row, etc.
    try:
        df = pd.read_excel(file_path)
        
        # Assuming structure has columns like:
        # - No (order)
        # - Section/Category
        # - Item Name
        
        items = []
        section_name = "General"  # Default section
        
        for idx, row in df.iterrows():
            # Adjust column names based on actual Excel
            # This is a template - modify according to your Excel structure
            
            # Example: If Excel has "Category" and "Item" columns
            if pd.notna(row.get('Category')):
                section_name = row['Category']
            
            if pd.notna(row.get('Item')):
                items.append({
                    'vehicle_type': VehicleType.EV,
                    'section_name': section_name,
                    'item_name': row['Item'],
                    'item_order': idx + 1
                })
        
        print(f"✅ Found {len(items)} EV checklist items")
        return items
        
    except Exception as e:
        print(f"❌ Error parsing EV checklist: {str(e)}")
        return []


def parse_lv_checklist(file_path: str) -> list[dict]:
    """
    Parse LV checklist from Excel file.
    LV checklist also applies to DC and BIS types.
    
    Args:
        file_path: Path to LV Excel file
        
    Returns:
        List of checklist items
    """
    print(f"📖 Reading LV checklist from: {file_path}")
    
    try:
        df = pd.read_excel(file_path)
        
        items = []
        section_name = "General"
        
        for idx, row in df.iterrows():
            # Adjust based on actual Excel structure
            if pd.notna(row.get('Category')):
                section_name = row['Category']
            
            if pd.notna(row.get('Item')):
                item_data = {
                    'section_name': section_name,
                    'item_name': row['Item'],
                    'item_order': idx + 1
                }
                
                # Create for LV, DC, and BIS
                for vtype in [VehicleType.LV, VehicleType.DC, VehicleType.BIS]:
                    items.append({
                        **item_data,
                        'vehicle_type': vtype
                    })
        
        print(f"✅ Found {len(items)} checklist items (LV/DC/BIS)")
        return items
        
    except Exception as e:
        print(f"❌ Error parsing LV checklist: {str(e)}")
        return []


def populate_checklist_templates(db: Session, items: list[dict]):
    """
    Populate checklist_templates table with parsed items.
    
    Args:
        db: Database session
        items: List of checklist items to insert
    """
    print(f"💾 Populating database with {len(items)} items...")
    
    # Clear existing items (optional)
    # db.query(ChecklistTemplate).delete()
    
    for item in items:
        checklist_item = ChecklistTemplate(**item)
        db.add(checklist_item)
    
    db.commit()
    print("✅ Database populated successfully!")


def main():
    """Main entry point"""
    print("🚀 Starting P2H Checklist Parser...")
    print("=" * 60)
    
    # Get project root
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs"
    
    # File paths
    ev_file = docs_dir / "Form P2H Unit EV.xlsx"
    lv_file = docs_dir / "P2h Unit LV.xlsx"
    
    # Check if files exist
    if not ev_file.exists():
        print(f"❌ File not found: {ev_file}")
        return
    
    if not lv_file.exists():
        print(f"❌ File not found: {lv_file}")
        return
    
    # Parse Excel files
    all_items = []
    
    # Parse EV checklist
    ev_items = parse_ev_checklist(str(ev_file))
    all_items.extend(ev_items)
    
    # Parse LV checklist (also for DC and BIS)
    lv_items = parse_lv_checklist(str(lv_file))
    all_items.extend(lv_items)
    
    print("=" * 60)
    print(f"📊 Total items to insert: {len(all_items)}")
    
    # Populate database
    db = SessionLocal()
    try:
        populate_checklist_templates(db, all_items)
    except Exception as e:
        print(f"❌ Error populating database: {str(e)}")
        db.rollback()
    finally:
        db.close()
    
    print("=" * 60)
    print("🎉 Checklist parsing complete!")
    print("\nNext steps:")
    print("1. Verify data: SELECT * FROM checklist_templates;")
    print("2. Test API: GET /p2h/checklist/EV")
    print("3. Test API: GET /p2h/checklist/LV")


if __name__ == "__main__":
    main()
