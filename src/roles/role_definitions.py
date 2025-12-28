"""
Role definitions and data structures
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml

from src.utils.logger import get_logger


@dataclass
class RoleSkills:
    """Skills categorization for a role."""
    core: List[str] = field(default_factory=list)  # Must-have skills
    important: List[str] = field(default_factory=list)  # Should-have skills
    bonus: List[str] = field(default_factory=list)  # Nice-to-have skills


@dataclass
class RoleDefinition:
    """Complete definition of a job role."""
    
    # Basic info
    role_id: str
    role_name: str
    description: str = ""
    
    # Section weights (override defaults)
    section_weights: Dict[str, float] = field(default_factory=dict)
    
    # Skills categorization
    skills: RoleSkills = field(default_factory=RoleSkills)
    
    # Keywords for role detection and scoring
    keywords: List[str] = field(default_factory=list)
    
    # Minimum experience expectations
    min_years_experience: Optional[int] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_section_weight(self, section_name: str, default: float = 0.0) -> float:
        """
        Get section weight for this role.
        
        Args:
            section_name: Name of section
            default: Default weight if not specified
            
        Returns:
            Section weight
        """
        return self.section_weights.get(section_name, default)
    
    def get_all_skills(self) -> List[str]:
        """Get all skills (core + important + bonus)."""
        return self.skills.core + self.skills.important + self.skills.bonus
    
    def get_required_skills(self) -> List[str]:
        """Get required skills (core only)."""
        return self.skills.core
    
    def is_core_skill(self, skill: str) -> bool:
        """Check if skill is core requirement."""
        return skill.lower() in [s.lower() for s in self.skills.core]
    
    def is_important_skill(self, skill: str) -> bool:
        """Check if skill is important."""
        return skill.lower() in [s.lower() for s in self.skills.important]
    
    def is_bonus_skill(self, skill: str) -> bool:
        """Check if skill is bonus."""
        return skill.lower() in [s.lower() for s in self.skills.bonus]


class RoleManager:
    """Manages role definitions and loading."""
    
    def __init__(self, roles_dir: Optional[Path] = None):
        """
        Initialize role manager.
        
        Args:
            roles_dir: Directory containing role YAML files
        """
        self.logger = get_logger(__name__)
        
        if roles_dir is None:
            from src.config.settings import get_settings
            settings = get_settings()
            roles_dir = Path(settings.get('paths.roles_dir', 'data/roles'))
        
        self.roles_dir = Path(roles_dir)
        self.roles: Dict[str, RoleDefinition] = {}
        
        if self.roles_dir.exists():
            self._load_roles()
        else:
            self.logger.warning(f"Roles directory not found: {self.roles_dir}")
    
    def _load_roles(self) -> None:
        """Load all role definitions from YAML files."""
        yaml_files = list(self.roles_dir.glob("*.yaml")) + list(self.roles_dir.glob("*.yml"))
        
        for yaml_file in yaml_files:
            try:
                role = self._load_role_from_file(yaml_file)
                self.roles[role.role_id] = role
                self.logger.info(f"Loaded role: {role.role_name} ({role.role_id})")
            except Exception as e:
                self.logger.error(f"Failed to load role from {yaml_file}: {e}")
        
        self.logger.info(f"Loaded {len(self.roles)} role definitions")
    
    def _load_role_from_file(self, file_path: Path) -> RoleDefinition:
        """
        Load role definition from YAML file.
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            RoleDefinition object
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Parse skills
        skills_data = data.get('skills', {})
        skills = RoleSkills(
            core=skills_data.get('core', []),
            important=skills_data.get('important', []),
            bonus=skills_data.get('bonus', [])
        )
        
        # Create role definition
        role = RoleDefinition(
            role_id=data.get('role_id', file_path.stem),
            role_name=data.get('role_name', ''),
            description=data.get('description', ''),
            section_weights=data.get('section_weights', {}),
            skills=skills,
            keywords=data.get('keywords', []),
            min_years_experience=data.get('min_years_experience'),
            metadata=data.get('metadata', {})
        )
        
        return role
    
    def get_role(self, role_id: str) -> Optional[RoleDefinition]:
        """
        Get role definition by ID.
        
        Args:
            role_id: Role identifier
            
        Returns:
            RoleDefinition or None if not found
        """
        return self.roles.get(role_id)
    
    def list_roles(self) -> List[str]:
        """Get list of available role IDs."""
        return list(self.roles.keys())
    
    def get_all_roles(self) -> Dict[str, RoleDefinition]:
        """Get all role definitions."""
        return self.roles.copy()