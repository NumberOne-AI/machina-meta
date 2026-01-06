# DevOps Skills for Claude Code

This document catalogs available Claude Code skills for DevOps tools and workflows relevant to the machina-meta workspace.

**Last Updated:** 2026-01-06

## Overview

Claude Code skills are modular capabilities that extend Claude's functionality for specific tasks or domains. Each skill is defined by a `SKILL.md` file containing instructions, examples, and reference documentation.

Skills use ~100 tokens during metadata scanning and ~5k tokens when activated, making them efficient for specialized tasks.

## Installation

Skills can be installed from git repositories using plugin marketplace commands:

```bash
# Add a marketplace
/plugin marketplace add https://github.com/ahmedasmar/devops-claude-skills
/plugin marketplace add https://github.com/mhattingpete/claude-skills-marketplace
/plugin marketplace add https://github.com/langpingxue/atlassian-skills

# Install specific skills
/plugin install gitops-workflows@devops-skills
/plugin install git-pushing@claude-skills-marketplace
/plugin install atlassian-skills@atlassian-skills
```

## Git & Version Control

### git-pushing

**Source:** [mhattingpete/claude-skills-marketplace](https://github.com/mhattingpete/claude-skills-marketplace)

**Description:** Automatically stage, commit with conventional commit messages, and push changes to remote.

**Use Cases:**
- Automating git workflows
- Enforcing conventional commit standards
- Streamlining push operations

**Installation:**
```bash
/plugin marketplace add https://github.com/mhattingpete/claude-skills-marketplace
/plugin install git-pushing@claude-skills-marketplace
```

## GitHub

### github-pr-review-operation

**Source:** [Community skill](https://dev.to/shibayu36/i-created-claude-skills-for-convenient-pull-request-review-operations-from-claude-code-d7p)

**Description:** Specialized skill for pull request review operations, solving issues with AI autonomous review of PRs.

**Use Cases:**
- PR review automation
- Code quality checks
- Review feedback implementation

### GitHub MCP Server

**Source:** Docker MCP Toolkit

**Description:** Access repository history, review code changes, execute git commands, create pull requests.

**Features:**
- Repository history access
- Code change review
- Git command execution
- PR creation and management

**Setup:** Available through Docker MCP Toolkit integration

### Official GitHub Actions Integration

**Source:** [Claude Code Docs](https://code.claude.com/docs/en/github-actions)

**Repository:** [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action)

**Description:** Official GitHub action for PRs and issues that intelligently detects when to activate based on workflow context.

**Use Cases:**
- Automated PR responses
- Issue triage
- CI/CD integration

## Jira & Atlassian

### atlassian-skills

**Source:** [langpingxue/atlassian-skills](https://github.com/langpingxue/atlassian-skills)

**Description:** Full read/write access to Jira, Confluence, and Bitbucket with comprehensive API coverage.

**Jira Capabilities:**
- Issue management
- JQL search
- Workflows
- Agile boards
- Sprints
- Worklogs

**Confluence Capabilities:**
- Page management
- CQL search
- Comments
- Labels

**Bitbucket Capabilities:**
- Projects and repositories
- Pull requests
- Code search
- Commit history

**Features:**
- Supports Cloud & Data Center deployments
- Dual Authentication: Cloud (API Token) and Data Center (PAT Token)
- 45 total methods with 203 test cases
- Unified JSON response formatting

**Installation:**
```bash
/plugin marketplace add https://github.com/langpingxue/atlassian-skills
/plugin install atlassian-skills@atlassian-skills
```

### atlassian-readonly-skills

**Source:** [langpingxue/atlassian-skills](https://github.com/langpingxue/atlassian-skills)

**Description:** Read-only variant for reduced token consumption and preventing accidental modifications.

**Use Cases:**
- Query-only access
- Reporting and analytics
- Risk-free exploration

**Installation:**
```bash
/plugin install atlassian-readonly-skills@atlassian-skills
```

### Atlassian MCP Server

**Source:** [Velir Integration Guide](https://www.velir.com/ideas/2025/06/05/ai-development-integrating-atlassian-jira-with-claude-code)

**Description:** MCP server integration for Jira workflow automation.

**Use Cases:**
- Creating Jira tickets from code analysis
- Converting TODO comments to tracked tickets
- Automated tech debt tracking
- Issue lifecycle management

## ArgoCD & GitOps

### gitops-workflows

**Source:** [ahmedasmar/devops-claude-skills](https://github.com/ahmedasmar/devops-claude-skills)

**Description:** ArgoCD and Flux CD implementation with production-ready templates and automation scripts.

**Features:**
- 8 Python automation scripts
- Production-ready templates:
  - ArgoCD 3.x installation
  - Flux bootstrap
  - ApplicationSets
- Modern secrets management (sealed-secrets, external-secrets)
- Multi-cluster deployment patterns with ApplicationSets
- ArgoCD 3.x and Flux 2.7 (2024-2025) updates

**Use Cases:**
- GitOps workflow setup
- Multi-cluster deployments
- Application lifecycle management
- Secrets management

**Installation:**
```bash
/plugin marketplace add https://github.com/ahmedasmar/devops-claude-skills
/plugin install gitops-workflows@devops-skills
```

### Kubernetes Claude MCP Server

**Source:** [blankcut-kubernetes-claude](https://playbooks.com/mcp/blankcut-kubernetes-claude)

**Description:** Integrates Claude with Kubernetes, ArgoCD, and GitLab to analyze and troubleshoot GitOps workflows.

**Features:**
- Collects resource information across K8s, ArgoCD, GitLab
- Correlates cross-system data
- Provides actionable recommendations
- GitOps workflow analysis

### Claude Kubernetes MCP Server (Advanced)

**Source:** [AI Base MCP Server](https://mcp.aibase.com/server/1916355113240207362)

**Description:** Advanced K8s control and automation based on Go integration with ArgoCD support.

**Features:**
- Advanced Kubernetes control
- ArgoCD integration
- Go-based implementation
- Automation capabilities

## Kubernetes

### kubernetes (Installed)

**Source:** machina-meta workspace (`.claude/skills/kubernetes/`)

**Status:** ✅ Already installed in workspace

**Description:** Comprehensive Kubernetes support generated from official documentation.

**Coverage:**
- kubectl commands and API resources
- Deployments, StatefulSets, Jobs, CronJobs
- Services, networking, DNS
- Persistent storage configuration
- RBAC, Secrets, encryption
- Troubleshooting and operations

**Reference Files:**
- `references/api.md` - Complete API reference
- `references/concepts.md` - Core concepts
- `references/configuration.md` - Best practices
- `references/getting_started.md` - Tutorials
- `references/security.md` - Security policies
- `references/services.md` - Networking
- `references/storage.md` - Storage classes
- `references/workloads.md` - Workload resources
- `references/tasks.md` - Step-by-step guides
- `references/tutorials.md` - End-to-end tutorials

**Use Cases:**
- Writing/modifying YAML manifests
- kubectl command assistance
- Cluster operations and troubleshooting
- Networking and service discovery
- Security configuration

### k8s-troubleshooter

**Source:** [ahmedasmar/devops-claude-skills](https://github.com/ahmedasmar/devops-claude-skills)

**Description:** Kubernetes diagnostics with cluster health checks, pod diagnostics, and structured incident response playbooks.

**Features:**
- Cluster health checks
- Pod diagnostics
- Incident response playbooks
- Deployment issue resolution

**Use Cases:**
- Debugging pod failures
- Cluster health monitoring
- Incident response
- Performance troubleshooting

**Installation:**
```bash
/plugin install k8s-troubleshooter@devops-skills
```

## Google Cloud Platform (GKE & gcloud)

### devops (GCP-focused)

**Source:** [mrgoonie/claudekit-skills](https://github.com/mrgoonie/claudekit-skills)

**Description:** Deploy and manage cloud infrastructure on Google Cloud Platform.

**GCP Services:**
- Compute Engine
- Google Kubernetes Engine (GKE)
- Cloud Run
- App Engine
- Cloud Storage

**Features:**
- Serverless functions deployment
- Edge computing configuration
- Container management
- CI/CD pipeline setup
- Cloud infrastructure cost optimization

**Use Cases:**
- GKE cluster management
- Serverless deployments
- Infrastructure provisioning
- Cost optimization
- Multi-service orchestration

### Official Vertex AI Integration

**Source:** [Claude Code Docs](https://docs.claude.com/en/docs/claude-code/google-vertex-ai)

**Description:** Official integration for running Claude Code using models in Google Cloud Vertex AI.

**Setup Requirements:**
1. Configure `ANTHROPIC_VERTEX_PROJECT_ID` environment variable
2. Assign IAM permissions:
   - `roles/aiplatform.user` role
   - `aiplatform.endpoints.predict` permission
3. Authenticate using gcloud CLI:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

**Resources:**
- [Step-by-step guide](https://medium.com/@dan.avila7/step-by-step-guide-to-connect-claude-code-with-google-cloud-vertex-ai-17e7916e711e)
- [Using Claude Code with Vertex AI](https://medium.com/google-cloud/claude-code-on-google-vertex-ai-25e13b1b643d)
- [Supercharge ADK Development](https://medium.com/google-cloud/supercharge-adk-development-with-claude-code-skills-d192481cbe72)

## Docker

### docker-containerization

**Source:** [claude-plugins.dev](https://claude-plugins.dev/skills/@ailabs-393/ai-labs-claude-skills/docker-containerization)

**Description:** Comprehensive Docker support for containerizing applications.

**Features:**
- Dockerfile creation and optimization
- docker-compose setup
- Bash scripts for container management
- Deployment guides for orchestration platforms
- Multi-stage builds
- Container optimization
- Docker networking
- Volume management
- Container security

**Use Cases:**
- Containerizing Next.js, React, Node.js applications
- Development environment setup
- Production containerization
- CI/CD pipeline integration
- Microservices deployment

### docker-containerization-skill (Advanced)

**Source:** [claude-plugins.dev](https://claude-plugins.dev/skills/@Useforclaude/skills-claude/docker-containerization-skill)

**Description:** Advanced containerization with Kubernetes integration.

**Features:**
- Dockerfile creation
- docker-compose configurations
- Multi-stage builds
- Container optimization
- Docker networking and volumes
- Kubernetes basics integration
- Container security
- CI/CD integration
- Microservices deployment
- Production-ready containerization strategies

### Docker MCP Toolkit

**Source:** [Docker Official Docs](https://docs.docker.com/guides/genai-claude-code-mcp/claude-code-mcp-guide/)

**Description:** Generate Docker Compose files with natural language using Model Context Protocol.

**Features:**
- Search Docker Hub images
- Generate complete Docker Compose stacks
- Natural language stack description
- Production-ready Compose file generation

**Use Cases:**
- Rapid stack prototyping
- Infrastructure as code generation
- Multi-service orchestration
- Development environment automation

### Development Containers

**Source:** [Claude Code Docs](https://code.claude.com/docs/en/devcontainer)

**Description:** Pre-configured development container support.

**Features:**
- VS Code Dev Containers extension compatible
- Customizable devcontainer configurations
- Reproducible development environments

**Resources:**
- [ClaudeBox](https://github.com/RchGrav/claudebox) - Full containerized development environment
- [Building with Claude Code and Docker Compose](https://shipyard.build/blog/building-an-app-claude-code-docker-compose/)
- [Running Claude Code in Docker](https://medium.com/rigel-computer-com/running-claude-code-in-docker-containers-one-project-one-container-1601042bf49c)

## Additional DevOps Skills

### iac-terraform

**Source:** [ahmedasmar/devops-claude-skills](https://github.com/ahmedasmar/devops-claude-skills)

**Description:** Infrastructure as Code focused on Terraform and Terragrunt configurations.

**Features:**
- Terraform module creation and validation
- Terragrunt configuration
- State management troubleshooting
- Best practices enforcement

**Installation:**
```bash
/plugin install iac-terraform@devops-skills
```

### ci-cd

**Source:** [ahmedasmar/devops-claude-skills](https://github.com/ahmedasmar/devops-claude-skills)

**Description:** Pipeline development and optimization for multiple CI/CD platforms.

**Supported Platforms:**
- GitHub Actions
- GitLab CI
- Other popular CI/CD platforms

**Features:**
- Pipeline creation and optimization
- Performance tuning
- Security enhancements
- Best practices implementation

**Installation:**
```bash
/plugin install ci-cd@devops-skills
```

### monitoring-observability

**Source:** [ahmedasmar/devops-claude-skills](https://github.com/ahmedasmar/devops-claude-skills)

**Description:** Observability strategy implementation with Prometheus and OpenTelemetry.

**Features:**
- Prometheus alerts for web apps and Kubernetes
- OpenTelemetry collector configuration
- SLO calculation tools
- Monitoring best practices

**Installation:**
```bash
/plugin install monitoring-observability@devops-skills
```

### aws-cost-optimization

**Source:** [ahmedasmar/devops-claude-skills](https://github.com/ahmedasmar/devops-claude-skills)

**Description:** AWS financial operations with automated cost analysis.

**Features:**
- 6 automated analysis scripts
- Identifies waste and optimization opportunities
- Reserved Instance analysis
- Cost anomaly detection
- Coverage across EC2, RDS, EBS, S3

**Installation:**
```bash
/plugin install aws-cost-optimization@devops-skills
```

## Skill Collections & Marketplaces

### Official & Community Repositories

| Repository | Description | URL |
|------------|-------------|-----|
| **anthropics/skills** | Official Anthropic skills repository | [GitHub](https://github.com/anthropics/skills) |
| **ahmedasmar/devops-claude-skills** | DevOps-focused marketplace with ArgoCD, K8s, Terraform, CI/CD | [GitHub](https://github.com/ahmedasmar/devops-claude-skills) |
| **mhattingpete/claude-skills-marketplace** | Software engineering workflows including git automation | [GitHub](https://github.com/mhattingpete/claude-skills-marketplace) |
| **langpingxue/atlassian-skills** | Comprehensive Jira, Confluence, Bitbucket integration | [GitHub](https://github.com/langpingxue/atlassian-skills) |
| **alirezarezvani/claude-skills** | Real-world usage skills including Jira ticket automation | [GitHub](https://github.com/alirezarezvani/claude-skills) |
| **obra/superpowers** | 20+ battle-tested core skills library | [GitHub](https://github.com/obra/superpowers) |
| **obra/superpowers-lab** | Experimental skills for Claude Code | [GitHub](https://github.com/obra/superpowers-lab) |
| **travisvn/awesome-claude-skills** | Curated list of awesome Claude Skills | [GitHub](https://github.com/travisvn/awesome-claude-skills) |
| **ComposioHQ/awesome-claude-skills** | Another curated list with marketplace integrations | [GitHub](https://github.com/ComposioHQ/awesome-claude-skills) |
| **SkillsMP.com** | Browse 25,000+ agent skills compatible with Claude Code | [Website](https://skillsmp.com/) |

### mhattingpete/claude-skills-marketplace Skills

Additional skills from this marketplace:

- **test-fixing**: Systematically identifies and fixes failing tests using smart error grouping
- **review-implementing**: Processes and implements code review feedback with todo tracking
- **code-execution**: Executes Python code locally with marketplace API access (90%+ token savings)
- **code-transfer**: Transfers code between files with line-based precision
- **code-refactor**: Performs bulk code refactoring operations
- **file-operations**: Analyzes files and gets detailed metadata
- **feature-planning**: Breaks down feature requests into implementable plans
- **conversation-analyzer**: Analyzes Claude Code conversation history
- **code-auditor**: Comprehensive codebase analysis
- **codebase-documenter**: Generates documentation explaining how codebases work
- **project-bootstrapper**: Sets up new projects with best practices

## Related Documentation

- [CLAUDE.md](../CLAUDE.md) - Workspace-level guidance for Claude Code
- [DEVOPS.md](DEVOPS.md) - DevOps workflows, preview environments, CI/CD
- [LLM.md](LLM.md) - LLM integration and prompt engineering
- [repos/dem2-infra/](../repos/dem2-infra/) - Infrastructure deployment with ArgoCD

## Contributing Skills

To create custom skills for machina-meta:

1. Create a skill directory in `.claude/skills/<skill-name>/`
2. Write a `SKILL.md` file with:
   - YAML frontmatter (name, description)
   - Instructions and usage guidelines
   - Examples and reference documentation
3. Test the skill thoroughly
4. Submit a PR if contributing to community marketplaces

### Skill Format

```yaml
---
name: skill-name
description: Brief description of what the skill does
---

# Skill Name

Detailed instructions and documentation...
```

## References

- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [DevOps Claude Skills](https://github.com/ahmedasmar/devops-claude-skills)
- [Atlassian Skills](https://github.com/langpingxue/atlassian-skills)
- [Claude Skills Marketplace](https://github.com/mhattingpete/claude-skills-marketplace)
- [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions)
- [Docker MCP Toolkit Guide](https://docs.docker.com/guides/genai-claude-code-mcp/claude-code-mcp-guide/)
- [Claude Code on Vertex AI](https://docs.claude.com/en/docs/claude-code/google-vertex-ai)
- [Kubernetes MCP Server](https://playbooks.com/mcp/blankcut-kubernetes-claude)
- [Jira Integration Guide](https://www.velir.com/ideas/2025/06/05/ai-development-integrating-atlassian-jira-with-claude-code)
- [Claude Code Plugin Marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills)
- [SkillsMP Marketplace](https://skillsmp.com/)

---

**Version:** 1.0.0
**Last Updated:** 2026-01-06
