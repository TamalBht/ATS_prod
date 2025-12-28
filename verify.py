"""
Verify Phase 3 installation
"""

import sys
import inspect

print("=" * 70)
print("PHASE 3 VERIFICATION")
print("=" * 70)

# Check imports
try:
    from src.scoring.ats_scorer import ATSScorer
    print("\n✓ ATSScorer imported successfully")
    
    # Check __init__ signature
    sig = inspect.signature(ATSScorer.__init__)
    params = list(sig.parameters.keys())
    print(f"  __init__ parameters: {params}")
    
    if 'role_id' in params:
        print("  ✓ role_id parameter present")
    else:
        print("  ✗ role_id parameter MISSING")
        print("  → You need to update src/scoring/ats_scorer.py")
    
except Exception as e:
    print(f"\n✗ Error importing ATSScorer: {e}")

# Check role modules
try:
    from src.roles.role_definitions import RoleManager
    from src.roles.role_matcher import RoleMatcher
    from src.roles.role_scorer import RoleScorer
    print("\n✓ Role modules imported successfully")
except Exception as e:
    print(f"\n✗ Error importing role modules: {e}")

# Check role files
from pathlib import Path

roles_dir = Path("data/roles")
if roles_dir.exists():
    role_files = list(roles_dir.glob("*.yaml"))
    print(f"\n✓ Found {len(role_files)} role definition files:")
    for rf in role_files:
        print(f"  - {rf.name}")
else:
    print(f"\n✗ Roles directory not found: {roles_dir}")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)