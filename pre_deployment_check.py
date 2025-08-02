#!/usr/bin/env python3
"""
Pre-Deployment Checklist
Verify everything is ready for production deployment
"""

import os
import subprocess
import json
from pathlib import Path

class PreDeploymentChecker:
    def __init__(self):
        self.checks = {
            "git_initialized": False,
            "all_files_committed": False,
            "requirements_file": False,
            "env_example": False,
            "render_yaml": False,
            "github_workflow": False,
            "tests_created": False,
            "documentation": False
        }
    
    def check_git_status(self):
        """Check if git is initialized and clean"""
        print("\n1. Checking Git Status...")
        try:
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.checks["git_initialized"] = True
                if not result.stdout.strip():
                    self.checks["all_files_committed"] = True
                    print("   [OK] Git repository is clean")
                else:
                    print("   [WARNING] Uncommitted changes:")
                    print(result.stdout)
            else:
                print("   [ERROR] Git not initialized")
        except:
            print("   [ERROR] Git command failed")
    
    def check_files(self):
        """Check required files exist"""
        print("\n2. Checking Required Files...")
        
        files_to_check = {
            "requirements.txt": "requirements_file",
            "render.yaml": "render_yaml",
            ".github/workflows/deploy.yml": "github_workflow"
        }
        
        for file, check_key in files_to_check.items():
            if os.path.exists(file):
                self.checks[check_key] = True
                print(f"   [OK] {file}")
            else:
                print(f"   [MISSING] {file}")
        
        # Check for env example
        if os.path.exists("env.example") or os.path.exists(".env.example"):
            self.checks["env_example"] = True
            print("   [OK] Environment example file")
        else:
            print("   [MISSING] env.example file")
    
    def check_tests(self):
        """Check if tests exist"""
        print("\n3. Checking Tests...")
        
        test_files = [
            "test_mlb_league_import.py",
            "import_my_mlb_league.py",
            "import_league_by_url.py"
        ]
        
        found = sum(1 for f in test_files if os.path.exists(f))
        if found > 0:
            self.checks["tests_created"] = True
            print(f"   [OK] Found {found} test files")
        else:
            print("   [WARNING] No test files found")
    
    def check_documentation(self):
        """Check documentation"""
        print("\n4. Checking Documentation...")
        
        docs = [
            "README.md",
            "CLAUDE.md",
            "MLB_IMPORT_TEST_GUIDE.md",
            "RENDER_DEPLOYMENT.md"
        ]
        
        found = sum(1 for f in docs if os.path.exists(f))
        if found >= 2:
            self.checks["documentation"] = True
            print(f"   [OK] Found {found} documentation files")
        else:
            print("   [WARNING] Limited documentation")
    
    def generate_report(self):
        """Generate deployment readiness report"""
        print("\n" + "="*60)
        print("DEPLOYMENT READINESS REPORT")
        print("="*60)
        
        passed = sum(1 for v in self.checks.values() if v)
        total = len(self.checks)
        
        print(f"\nScore: {passed}/{total} checks passed")
        print("-"*60)
        
        for check, passed in self.checks.items():
            status = "✓" if passed else "✗"
            print(f"[{status}] {check.replace('_', ' ').title()}")
        
        print("\n" + "="*60)
        
        if passed == total:
            print("🚀 READY FOR DEPLOYMENT!")
            print("\nNext steps:")
            print("1. Create GitHub repository: https://github.com/new")
            print("2. Push code: git push -u origin main")
            print("3. Deploy to Render.com")
            print("4. Update Yahoo redirect URI")
        else:
            print("⚠️  Some checks failed. Fix these before deploying.")
            
            if not self.checks["all_files_committed"]:
                print("\nRun: git add . && git commit -m 'Ready for deployment'")
    
    def save_report(self):
        """Save deployment checklist"""
        report = {
            "checks": self.checks,
            "ready": all(self.checks.values()),
            "score": f"{sum(1 for v in self.checks.values() if v)}/{len(self.checks)}"
        }
        
        with open("deployment_readiness.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\nDetailed report saved to: deployment_readiness.json")

def main():
    print("Pre-Deployment Check for Fantasy AI")
    print("="*60)
    
    checker = PreDeploymentChecker()
    
    # Run all checks
    checker.check_git_status()
    checker.check_files()
    checker.check_tests()
    checker.check_documentation()
    
    # Generate report
    checker.generate_report()
    checker.save_report()

if __name__ == "__main__":
    main()