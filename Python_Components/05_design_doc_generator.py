from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from jinja2 import Template
import os
import traceback
from datetime import datetime
import re
from collections import defaultdict

class DesignDocumentGenerator:
    def __init__(self, vector_store_path='./vector_store/'):
        self.vector_store_path = vector_store_path
        self._embeddings = None
        self._processor = None
        self._vectorstore = None
        
        # Enhanced template with better structure and RAG integration
        self.design_doc_template = '''# {{title}}

**Document Type:** Technical Design Document
**Generated:** {{timestamp}}
**Version:** 1.0
**Status:** Draft

---

## 1. Executive Summary
{{overview}}

## 2. Background and Context
{{background}}

## 3. Requirements Analysis
{{requirements}}

## 4. System Architecture
{{architecture}}

## 5. Technical Implementation
{{implementation}}

## 6. Data Flow and Integration
{{data_flow}}

## 7. Security Considerations
{{security}}

## 8. Performance and Scalability
{{performance}}

## 9. Testing Strategy
{{testing}}

## 10. Deployment Plan
{{deployment}}

## 11. Timeline and Milestones
{{timeline}}

## 12. Risk Assessment
{{risks}}

## 13. References and Sources
{{references}}

---
**Document Metadata:**
- Sources analyzed: {{source_count}} documents
- Content types: {{content_types}}
- Generated using RAG-enhanced analysis
- Last updated: {{timestamp}}
'''

    @property
    def embeddings(self):
        if self._embeddings is None:
            self._embeddings = HuggingFaceEmbeddings(
                model_name='sentence-transformers/all-MiniLM-L6-v2',
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        return self._embeddings

    @property
    def processor(self):
        if self._processor is None:
            try:
                from unified_processor_fast import UnifiedDataProcessor
            except ImportError:
                try:
                    from unified_processor import UnifiedDataProcessor
                except ImportError:
                    from unified_processor_fixed import UnifiedDataProcessor
            self._processor = UnifiedDataProcessor(self.vector_store_path)
        return self._processor

    @property
    def vectorstore(self):
        if self._vectorstore is None:
            self._vectorstore = self.processor.get_vectorstore()
        return self._vectorstore

    def _extract_relevant_content(self, user_request, k=10):
        """Extract and analyze relevant content from documents using RAG"""
        if not self.vectorstore:
            return [], {}, ""
        
        try:
            print(f"🔍 Searching for relevant content: {user_request}")
            # Search for relevant documents
            results = self.processor.search_documents(user_request, k=k)
            
            sources = []
            content_by_type = defaultdict(list)
            all_content = ""
            
            for doc, score in results:
                # Extract comprehensive metadata
                source_info = {
                    'title': doc.metadata.get('title', doc.metadata.get('file_name', 'Unknown')),
                    'type': doc.metadata.get('source', 'unknown'),
                    'score': float(score),
                    'url': doc.metadata.get('url', ''),
                    'page': doc.metadata.get('page', ''),
                    'content_preview': doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                }
                sources.append(source_info)
                
                # Group content by type for better analysis
                content_type = doc.metadata.get('source', 'unknown')
                content_by_type[content_type].append({
                    'title': source_info['title'],
                    'content': doc.page_content,
                    'score': score
                })
                
                # Accumulate all content for comprehensive analysis
                all_content += f"\n\n--- From {source_info['title']} ---\n{doc.page_content}"
            
            print(f"📚 Found {len(sources)} relevant sources across {len(content_by_type)} content types")
            return sources, dict(content_by_type), all_content
            
        except Exception as e:
            print(f"❌ Content extraction error: {e}")
            return [], {}, ""

    def _extract_key_terms(self, content, user_request):
        """Extract key technical terms and concepts from retrieved content"""
        technical_terms = []
        
        # Common technical patterns to look for in the content
        patterns = [
            r'\b(API|REST|GraphQL|microservice|database|authentication|authorization)\b',
            r'\b(Docker|Kubernetes|AWS|Azure|GCP|cloud)\b',
            r'\b(React|Angular|Vue|Node\.js|Python|Java|Go|JavaScript)\b',
            r'\b(PostgreSQL|MySQL|MongoDB|Redis|SQL)\b',
            r'\b(OAuth|JWT|SSL|TLS|HTTPS|security)\b',
            r'\b(CI/CD|DevOps|deployment|monitoring)\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            technical_terms.extend(matches)
        
        # Remove duplicates and return top terms
        return list(set(technical_terms))[:10]

    def _extract_requirements_from_content(self, content):
        """Extract functional and non-functional requirements from content"""
        requirements = {
            'functional': [],
            'non_functional': []
        }
        
        # Look for requirement patterns in the content
        func_patterns = [
            r'must\s+(be able to|support|provide|allow)\s+([^.]+)',
            r'shall\s+([^.]+)',
            r'requirement[s]?[:]?\s+([^.]+)',
            r'should\s+(be able to|support|provide|allow)\s+([^.]+)'
        ]
        
        for pattern in func_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                req = match if isinstance(match, str) else match[-1]
                if len(req.strip()) > 10:  # Only meaningful requirements
                    requirements['functional'].append(req.strip())
        
        # Non-functional requirements
        nf_patterns = [
            r'performance[:]?\s+([^.]+)',
            r'scalability[:]?\s+([^.]+)',
            r'security[:]?\s+([^.]+)',
            r'availability[:]?\s+([^.]+)',
            r'response time[:]?\s+([^.]+)'
        ]
        
        for pattern in nf_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            requirements['non_functional'].extend([match.strip() for match in matches if len(match.strip()) > 5])
        
        return requirements

    def _analyze_content_for_section(self, section_type, user_request, content_by_type, all_content):
        """Analyze retrieved content to generate contextual section content"""
        
        # Extract insights from the retrieved content
        key_terms = self._extract_key_terms(all_content, user_request)
        requirements = self._extract_requirements_from_content(all_content)
        
        if section_type == 'overview':
            return self._generate_contextual_overview(user_request, key_terms, content_by_type)
        elif section_type == 'background':
            return self._generate_contextual_background(user_request, all_content, content_by_type)
        elif section_type == 'requirements':
            return self._generate_contextual_requirements(user_request, requirements, key_terms)
        elif section_type == 'architecture':
            return self._generate_contextual_architecture(user_request, key_terms, content_by_type)
        elif section_type == 'implementation':
            return self._generate_contextual_implementation(user_request, key_terms, requirements)
        elif section_type == 'data_flow':
            return self._generate_data_flow_section(user_request, key_terms)
        elif section_type == 'security':
            return self._generate_security_section(user_request, key_terms)
        elif section_type == 'performance':
            return self._generate_performance_section(user_request, requirements)
        elif section_type == 'testing':
            return self._generate_testing_section(user_request, requirements)
        elif section_type == 'deployment':
            return self._generate_deployment_section(user_request, key_terms)
        elif section_type == 'timeline':
            return self._generate_timeline_section(user_request, requirements)
        elif section_type == 'risks':
            return self._generate_risks_section(user_request, key_terms)
        else:
            return f"Content for {section_type} will be developed based on detailed analysis."

    def _generate_contextual_overview(self, user_request, key_terms, content_by_type):
        """Generate overview using retrieved content context"""
        content_types = list(content_by_type.keys())
        
        overview = f"""This technical design document outlines the comprehensive approach for implementing: **{user_request}**

**Project Scope:**
Based on analysis of {len(content_by_type)} different content sources ({', '.join(content_types)}), this solution addresses the following key areas:

"""
        
        if key_terms:
            overview += f"""**Key Technologies Identified from Documentation:**
{', '.join(key_terms[:8])}

"""
        
        overview += f"""**Solution Approach:**
The design incorporates insights from existing organizational documentation and leverages identified best practices to ensure:
- Alignment with current technical standards and patterns
- Integration with existing systems and workflows
- Scalable and maintainable architecture based on proven approaches
- Security and compliance requirements derived from organizational standards

**Documentation Analysis:**
This design is informed by {sum(len(docs) for docs in content_by_type.values())} relevant documents from your knowledge base, ensuring contextual relevance and organizational alignment."""

        return overview

    def _generate_contextual_background(self, user_request, all_content, content_by_type):
        """Generate background section with context from retrieved documents"""
        
        background = f"""**Current State Analysis:**
The need for {user_request} has been identified through comprehensive analysis of existing documentation and organizational requirements.

**Context from Available Documentation:**
"""
        
        # Summarize content by type with actual insights
        for content_type, docs in content_by_type.items():
            if docs:
                # Get the highest scoring document for this type
                top_doc = max(docs, key=lambda x: x['score'])
                background += f"""
**{content_type.title()} Sources ({len(docs)} documents):**
- Primary insight: {top_doc['content'][:200]}...
- Relevance score: {top_doc['score']:.3f}
"""
        
        background += f"""
**Problem Statement:**
Based on the analyzed documentation, this design addresses the implementation of {user_request} while ensuring:
- Compatibility with existing systems and documented patterns
- Adherence to established organizational practices and standards
- Meeting identified business and technical requirements from multiple sources
- Leveraging existing knowledge and avoiding reinvention

**Stakeholder Requirements:**
The solution incorporates requirements and insights identified across {len(content_by_type)} different content types, ensuring comprehensive coverage of both functional and operational needs."""

        return background

    def _generate_contextual_requirements(self, user_request, requirements, key_terms):
        """Generate requirements based on extracted content"""
        req_section = f"""**Functional Requirements:**
Based on analysis of available documentation, the following functional requirements have been identified:

"""
        
        if requirements['functional']:
            for i, req in enumerate(requirements['functional'][:5], 1):
                req_section += f"{i}. {req}\n"
        else:
            req_section += f"""1. Core {user_request} functionality implementation
2. User interface and interaction requirements based on organizational standards
3. Data processing and management capabilities
4. Integration with existing systems and documented APIs
5. Reporting and monitoring features aligned with current practices
"""
        
        req_section += f"""
**Non-Functional Requirements:**
"""
        
        if requirements['non_functional']:
            for req in requirements['non_functional'][:5]:
                req_section += f"- {req}\n"
        else:
            req_section += """- Performance: Response time < 2 seconds for standard operations
- Scalability: Support for concurrent users and growing data volumes
- Availability: 99.9% uptime with minimal planned downtime
- Security: Industry-standard encryption and authentication
- Maintainability: Well-documented, modular code architecture
- Compliance: Adherence to organizational security and data policies
"""
        
        if key_terms:
            req_section += f"""
**Technology Requirements (from documentation analysis):**
- Integration with identified technologies: {', '.join(key_terms[:5])}
- Compatibility with existing technology stack
"""
        
        return req_section

    def _generate_contextual_architecture(self, user_request, key_terms, content_by_type):
        """Generate architecture section based on retrieved content"""
        
        arch_section = f"""**System Architecture Overview:**
The {user_request} solution follows a modern, scalable architecture designed to integrate with existing organizational systems and patterns.

**Core Components:**
1. **Presentation Layer**
   - User interface components following organizational design standards
   - API gateway and routing based on existing patterns
   - Authentication and session management integration

2. **Business Logic Layer**
   - Core {user_request} processing aligned with business rules
   - Workflow orchestration following documented processes
   - Service integration with existing business systems

3. **Data Layer**
   - Primary data storage using organizational standards
   - Caching mechanisms based on performance requirements
   - Data access patterns consistent with existing systems

4. **Integration Layer**
   - External system connectors for documented integrations
   - Message queuing and processing using established patterns
   - Event handling aligned with organizational event architecture

"""
        
        if key_terms:
            arch_section += f"""**Technology Stack (based on documentation analysis):**
- Identified technologies: {', '.join(key_terms[:6])}
- Architecture patterns: Microservices, API-first, Event-driven
- Integration approaches: RESTful APIs, Message queues, Event streaming
"""
        
        if content_by_type:
            arch_section += f"""
**Integration Context:**
Based on analysis of {len(content_by_type)} content types, the architecture ensures:
- Compatibility with existing {', '.join(content_by_type.keys())} systems
- Adherence to documented architectural patterns and standards
- Seamless integration with current technology ecosystem
"""
        
        return arch_section

    def _generate_contextual_implementation(self, user_request, key_terms, requirements):
        """Generate implementation section with retrieved content context"""
        
        impl_section = f"""**Implementation Strategy:**
The development of {user_request} will follow an iterative, risk-driven approach based on organizational best practices.

**Development Phases:**

**Phase 1: Foundation (Weeks 1-3)**
- Core infrastructure setup using identified technologies
- Basic {user_request} functionality implementation
- Database schema design based on documented data models
- Authentication framework integration with existing systems

**Phase 2: Core Features (Weeks 4-6)**
- Primary business logic implementation following documented patterns
- User interface development aligned with organizational standards
- API development using established conventions
- Integration with key systems identified in documentation

**Phase 3: Advanced Features (Weeks 7-8)**
- Advanced functionality based on extracted requirements
- Performance optimization using documented best practices
- Security implementation following organizational standards
- Comprehensive testing aligned with quality processes

**Phase 4: Deployment (Weeks 9-10)**
- Production environment setup using established patterns
- Deployment automation following organizational DevOps practices
- Monitoring and alerting integration with existing systems
- Documentation and training based on organizational standards

"""
        
        if key_terms:
            impl_section += f"""**Technology Implementation:**
Based on documentation analysis, implementation will leverage:
- Core technologies: {', '.join(key_terms[:4])}
- Development patterns: Following documented organizational standards
- Integration approaches: Using established APIs and protocols
"""
        
        impl_section += f"""
**Development Standards:**
- Code review processes aligned with organizational practices
- Automated testing following documented quality standards
- Continuous integration using established CI/CD pipelines
- Documentation standards consistent with organizational requirements
- Security practices based on documented security policies
"""
        
        return impl_section

    # Add placeholder methods for other sections
    def _generate_data_flow_section(self, user_request, key_terms):
        return f"""**Data Flow Architecture:**
The {user_request} system processes data through documented organizational patterns:

**Input Processing:**
- Data ingestion following established data pipeline patterns
- Validation using organizational data quality standards
- Transformation based on documented data models

**Core Processing:**
- Business logic execution aligned with documented processes
- State management using established patterns
- Event generation following organizational event architecture

**Output Generation:**
- Result formatting based on organizational standards
- Integration with existing reporting systems
- API responses following documented conventions

**Technology Integration:**
{f"- Leveraging identified technologies: {', '.join(key_terms[:4])}" if key_terms else "- Using organizational standard technology stack"}
- Following documented data architecture patterns
- Ensuring compliance with data governance policies
"""

    def _generate_security_section(self, user_request, key_terms):
        return f"""**Security Framework:**
The {user_request} implementation incorporates comprehensive security measures based on organizational standards:

**Authentication & Authorization:**
- Integration with existing identity management systems
- Role-based access control following organizational patterns
- Multi-factor authentication using established protocols
- Session management aligned with security policies

**Data Protection:**
- Encryption standards based on organizational requirements
- Data classification following documented policies
- Access controls aligned with data governance standards
- Audit logging using established security monitoring

**Application Security:**
- Security testing following organizational security practices
- Vulnerability management using established processes
- Code security reviews aligned with development standards
- Compliance with documented security policies

**Technology Security:**
{f"- Security implementation for identified technologies: {', '.join(key_terms[:3])}" if key_terms else "- Following organizational technology security standards"}
- Integration with existing security infrastructure
- Monitoring and alerting using established security tools
"""

    def _generate_performance_section(self, user_request, requirements):
        return f"""**Performance Requirements:**
The {user_request} system is designed for optimal performance based on organizational standards:

**Response Time Targets:**
- API responses: Following organizational SLA requirements
- User interface: Based on documented user experience standards
- Batch processing: Aligned with existing system performance expectations

**Scalability Design:**
- Horizontal scaling using established infrastructure patterns
- Load balancing following organizational deployment standards
- Auto-scaling based on documented capacity planning approaches

**Performance Optimization:**
- Caching strategies using organizational standard technologies
- Database optimization following documented best practices
- Monitoring integration with existing performance management systems

**Performance Testing:**
- Load testing using established testing frameworks
- Performance benchmarking against organizational standards
- Capacity planning following documented processes
"""

    def _generate_testing_section(self, user_request, requirements):
        return f"""**Testing Strategy:**
Comprehensive testing approach for {user_request} following organizational quality standards:

**Testing Framework:**
- Unit testing using established organizational frameworks
- Integration testing following documented testing patterns
- End-to-end testing aligned with quality assurance processes
- Performance testing using organizational standard tools

**Quality Assurance:**
- Code review processes following organizational standards
- Automated testing integration with existing CI/CD pipelines
- Test coverage requirements based on organizational policies
- Quality gates aligned with documented quality standards

**Test Automation:**
- Automated test execution using established testing infrastructure
- Regression testing following organizational testing practices
- Test reporting integration with existing quality management systems
"""

    def _generate_deployment_section(self, user_request, key_terms):
        return f"""**Deployment Strategy:**
The {user_request} system deployment follows organizational DevOps practices:

**Deployment Pipeline:**
- CI/CD integration with existing organizational pipelines
- Environment management following established patterns
- Deployment automation using organizational standard tools
- Release management aligned with documented processes

**Infrastructure:**
- Deployment using organizational standard infrastructure
- Monitoring integration with existing operational systems
- Backup and recovery following documented procedures
- Security compliance with organizational deployment standards

**Technology Deployment:**
{f"- Deployment of identified technologies: {', '.join(key_terms[:3])}" if key_terms else "- Using organizational standard deployment technologies"}
- Configuration management following established practices
- Environment consistency using documented deployment patterns
"""

    def _generate_timeline_section(self, user_request, requirements):
        return f"""**Project Timeline:**
Estimated timeline for {user_request} implementation based on organizational project management standards:

**Phase-based Timeline:**
- **Weeks 1-3**: Foundation and setup following organizational onboarding processes
- **Weeks 4-6**: Core development using established development practices
- **Weeks 7-8**: Integration and testing following organizational quality processes
- **Weeks 9-10**: Deployment using established deployment procedures

**Key Milestones:**
- Technical design approval: Following organizational review processes
- Development milestones: Aligned with organizational project management standards
- Testing completion: Based on documented quality gates
- Production deployment: Following organizational go-live procedures

**Risk Management:**
- Timeline risks managed using organizational project management practices
- Resource allocation following established resource management processes
- Dependency management aligned with organizational project coordination
"""

    def _generate_risks_section(self, user_request, key_terms):
        return f"""**Risk Assessment:**
Risk identification and mitigation for {user_request} based on organizational risk management practices:

**Technical Risks:**
- Integration complexity with existing systems
- Performance risks based on documented system constraints
- Security risks managed through organizational security practices
- Technology risks for identified technologies: {', '.join(key_terms[:3]) if key_terms else 'standard technology stack'}

**Project Risks:**
- Resource availability managed through organizational resource planning
- Timeline risks mitigated using established project management practices
- Scope management following organizational change control processes

**Mitigation Strategies:**
- Risk monitoring using organizational risk management tools
- Escalation procedures following documented organizational processes
- Contingency planning based on organizational risk management standards
- Regular risk reviews aligned with project management practices
"""

    def generate_design_document(self, user_request, title=None):
        """Generate enhanced design document using RAG content analysis"""
        start_time = datetime.now()
        
        # Generate title
        if not title:
            title = f"Technical Design Document: {user_request}"
        
        print(f"🔍 Analyzing relevant content for: {user_request}")
        
        # Extract relevant content from documents using RAG
        sources, content_by_type, all_content = self._extract_relevant_content(user_request, k=12)
        
        print(f"📚 Found {len(sources)} relevant sources across {len(content_by_type)} content types")
        
        # Generate sections using retrieved content context
        sections = {}
        section_types = [
            'overview', 'background', 'requirements', 'architecture', 
            'implementation', 'data_flow', 'security', 'performance', 
            'testing', 'deployment', 'timeline', 'risks'
        ]
        
        print("🤖 Generating contextual content sections...")
        for section_type in section_types:
            try:
                sections[section_type] = self._analyze_content_for_section(
                    section_type, user_request, content_by_type, all_content
                )
            except Exception as e:
                print(f"⚠️ Error generating {section_type}: {e}")
                sections[section_type] = f"Content for {section_type} section will be developed based on detailed analysis."
        
        # Format references with enhanced information
        references = self._format_enhanced_references(sources)
        content_types_str = ', '.join(content_by_type.keys()) if content_by_type else 'Various'
        
        # Template variables
        template_vars = {
            'title': title,
            'overview': sections['overview'],
            'background': sections['background'],
            'requirements': sections['requirements'],
            'architecture': sections['architecture'],
            'implementation': sections['implementation'],
            'data_flow': sections['data_flow'],
            'security': sections['security'],
            'performance': sections['performance'],
            'testing': sections['testing'],
            'deployment': sections['deployment'],
            'timeline': sections['timeline'],
            'risks': sections['risks'],
            'references': references,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source_count': len(sources),
            'content_types': content_types_str
        }
        
        # Generate document
        template = Template(self.design_doc_template)
        design_document = template.render(**template_vars)
        
        generation_time = (datetime.now() - start_time).total_seconds()
        
        print(f"✅ Enhanced document generated in {generation_time:.2f}s using {len(sources)} sources")
        
        return {
            'document': design_document,
            'sources': sources,
            'content_analysis': {
                'content_by_type': content_by_type,
                'total_content_length': len(all_content),
                'key_insights': f"Analyzed {len(sources)} documents across {len(content_by_type)} content types"
            },
            'metadata': {
                'title': title,
                'user_request': user_request,
                'timestamp': template_vars['timestamp'],
                'generation_time': f"{generation_time:.2f}s",
                'source_count': len(sources),
                'content_types': list(content_by_type.keys()),
                'rag_enhanced': True
            }
        }

    def _format_enhanced_references(self, sources):
        """Format references with detailed information from RAG analysis"""
        if not sources:
            return "No references available from the knowledge base."
        
        references = []
        
        # Group by content type for better organization
        by_type = defaultdict(list)
        for source in sources:
            by_type[source['type']].append(source)
        
        for content_type, type_sources in by_type.items():
            references.append(f"\n**{content_type.title()} Sources:**")
            for i, source in enumerate(type_sources, 1):
                ref = f"{i}. **{source['title']}**"
                if source.get('url'):
                    ref += f" - [Link]({source['url']})"
                if source.get('page'):
                    ref += f" (Page {source['page']})"
                ref += f" (Relevance: {source['score']:.3f})"
                
                # Add content preview for context
                if source.get('content_preview'):
                    ref += f"\n   Preview: {source['content_preview']}"
                
                references.append(ref)
        
        return '\n'.join(references)

    def save_design_document(self, document_data, filename=None):
        """Fast document saving"""
        if not filename:
            safe_title = ''.join(c for c in document_data['metadata']['title'] if c.isalnum() or c in (' ', '-', '_'))
            safe_title = safe_title.replace(' ', '_')[:30]  # Shorter filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'{safe_title}_{timestamp}.md'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(document_data['document'])
            print(f'✅ Document saved: {filename}')
            return filename
        except Exception as e:
            print(f'❌ Save error: {e}')
            return None

# Test function
def test_enhanced_generator():
    """Test the enhanced RAG-powered generator"""
    print("🧪 Testing Enhanced RAG Design Document Generator...")
    
    try:
        generator = DesignDocumentGenerator()
        
        # Test with a comprehensive request
        result = generator.generate_design_document(
            "User Authentication and Authorization System with OAuth2 Integration and Multi-Factor Authentication"
        )
        
        print(f"✅ Generated document with {result['metadata']['source_count']} sources")
        print(f"📄 Document length: {len(result['document'])} characters")
        print(f"⏱️ Generation time: {result['metadata']['generation_time']}")
        print(f"🔍 Content types analyzed: {', '.join(result['metadata']['content_types'])}")
        print(f"🤖 RAG enhanced: {result['metadata']['rag_enhanced']}")
        
        # Show content analysis summary
        if 'content_analysis' in result:
            print(f"📊 Content analysis: {result['content_analysis']['key_insights']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_enhanced_generator()