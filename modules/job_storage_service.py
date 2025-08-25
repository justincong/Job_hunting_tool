from typing import Dict, List, Any, Optional
from datetime import datetime
from .database_manager import db_manager

class JobAnalysisStorage:
    """Service for storing and retrieving job analysis data"""
    
    def __init__(self):
        self.collection = "job_analyses"
    
    def save_job_analysis(self, job_description: str, analysis: Dict[str, Any], 
                         job_title: str = None, company: str = None, 
                         job_url: str = None) -> str:
        """Save job analysis to database"""
        db = db_manager.get_database()
        if not db:
            raise Exception("Database not available")
        
        # Extract job title and company from analysis if not provided
        if not job_title and 'job_title' in analysis:
            job_title = analysis['job_title']
        if not company and 'company' in analysis:
            company = analysis['company']
        
        # Create document
        document = {
            'job_description': job_description,
            'job_title': job_title or 'Unknown Position',
            'company': company or 'Unknown Company',
            'job_url': job_url,
            'analysis': analysis,
            'tags': self._extract_tags(analysis),
            'skills_count': self._count_skills(analysis),
            'experience_level': analysis.get('experience_level', 'unknown')
        }
        
        return db.insert_document(self.collection, document)
    
    def get_job_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific job analysis by ID"""
        db = db_manager.get_database()
        if not db:
            return None
        
        return db.find_document_by_id(self.collection, analysis_id)
    
    def get_job_analyses(self, limit: int = 20, company: str = None, 
                        experience_level: str = None, skills: List[str] = None) -> List[Dict[str, Any]]:
        """Get job analyses with optional filtering"""
        db = db_manager.get_database()
        if not db:
            return []
        
        query = {}
        
        # Add filters
        if company:
            query['company'] = company
        if experience_level:
            query['experience_level'] = experience_level
        
        # For skills filtering, we'll do post-processing since it's complex
        analyses = db.find_documents(
            self.collection, 
            query=query, 
            limit=limit * 2 if skills else limit,  # Get more if we need to filter by skills
            sort_by='-created_at'
        )
        
        # Filter by skills if specified
        if skills:
            filtered_analyses = []
            for analysis in analyses:
                analysis_skills = self._get_all_skills(analysis.get('analysis', {}))
                if any(skill.lower() in [s.lower() for s in analysis_skills] for skill in skills):
                    filtered_analyses.append(analysis)
                    if len(filtered_analyses) >= limit:
                        break
            return filtered_analyses
        
        return analyses[:limit]
    
    def get_recent_analyses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent job analyses"""
        return self.get_job_analyses(limit=limit)
    
    def get_analyses_by_company(self, company: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get job analyses for a specific company"""
        return self.get_job_analyses(limit=limit, company=company)
    
    def get_analyses_by_experience_level(self, experience_level: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get job analyses for a specific experience level"""
        return self.get_job_analyses(limit=limit, experience_level=experience_level)
    
    def search_analyses(self, search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search job analyses by job title, company, or skills"""
        db = db_manager.get_database()
        if not db:
            return []
        
        # Get all analyses and filter in memory (simple implementation)
        # For production, you'd want to implement proper text search
        all_analyses = db.find_documents(self.collection, limit=100, sort_by='-created_at')
        
        search_term_lower = search_term.lower()
        matching_analyses = []
        
        for analysis in all_analyses:
            # Search in job title, company, and skills
            searchable_text = ' '.join([
                analysis.get('job_title', ''),
                analysis.get('company', ''),
                ' '.join(analysis.get('tags', [])),
                ' '.join(self._get_all_skills(analysis.get('analysis', {})))
            ]).lower()
            
            if search_term_lower in searchable_text:
                matching_analyses.append(analysis)
                if len(matching_analyses) >= limit:
                    break
        
        return matching_analyses
    
    def delete_job_analysis(self, analysis_id: str) -> bool:
        """Delete a job analysis"""
        db = db_manager.get_database()
        if not db:
            return False
        
        return db.delete_document(self.collection, analysis_id)
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get statistics about stored job analyses"""
        db = db_manager.get_database()
        if not db:
            return {}
        
        try:
            total_count = db.count_documents(self.collection)
            
            # Get recent analyses for stats
            recent_analyses = db.find_documents(self.collection, limit=100, sort_by='-created_at')
            
            # Calculate stats
            companies = set()
            experience_levels = {}
            top_skills = {}
            
            for analysis in recent_analyses:
                # Company stats
                if analysis.get('company'):
                    companies.add(analysis['company'])
                
                # Experience level stats
                exp_level = analysis.get('experience_level', 'unknown')
                experience_levels[exp_level] = experience_levels.get(exp_level, 0) + 1
                
                # Skills stats
                skills = self._get_all_skills(analysis.get('analysis', {}))
                for skill in skills:
                    top_skills[skill] = top_skills.get(skill, 0) + 1
            
            # Get top 10 skills
            top_skills_list = sorted(top_skills.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'total_analyses': total_count,
                'unique_companies': len(companies),
                'experience_levels': experience_levels,
                'top_skills': top_skills_list,
                'companies': list(companies)[:20]  # Top 20 companies
            }
        except Exception as e:
            print(f"Error getting analysis stats: {e}")
            return {}
    
    def _extract_tags(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract tags from analysis for easier searching"""
        tags = []
        
        # Add experience level as tag
        if analysis.get('experience_level'):
            tags.append(analysis['experience_level'])
        
        # Add industry as tag
        if analysis.get('industry'):
            tags.append(analysis['industry'])
        
        # Add top priority skills as tags
        priority_skills = analysis.get('priority_skills', [])
        for skill_info in priority_skills[:5]:  # Top 5 priority skills
            if isinstance(skill_info, dict) and 'skill' in skill_info:
                tags.append(skill_info['skill'])
            elif isinstance(skill_info, str):
                tags.append(skill_info)
        
        return tags
    
    def _count_skills(self, analysis: Dict[str, Any]) -> int:
        """Count total number of skills in analysis"""
        skills = self._get_all_skills(analysis)
        return len(skills)
    
    def _get_all_skills(self, analysis: Dict[str, Any]) -> List[str]:
        """Get all skills from analysis"""
        skills = []
        
        # Technical skills
        if 'technical_skills' in analysis:
            skills.extend(analysis['technical_skills'])
        
        # Soft skills
        if 'soft_skills' in analysis:
            skills.extend(analysis['soft_skills'])
        
        # Skills from nested structure
        if 'skills' in analysis:
            skill_data = analysis['skills']
            if isinstance(skill_data, dict):
                if 'technical' in skill_data:
                    skills.extend(skill_data['technical'])
                if 'soft' in skill_data:
                    skills.extend(skill_data['soft'])
        
        return list(set(skills))  # Remove duplicates

# Global instance
job_storage = JobAnalysisStorage()