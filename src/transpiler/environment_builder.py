from __future__ import annotations

import os
import json
from typing import Any, Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class GeneratedFile:
    """Represents a generated environment file."""
    path: str
    content: str
    description: str = ""
    file_type: str = "config"  # config, driver, pipeline, infrastructure


@dataclass
class EnvironmentMetadata:
    """Metadata about generated environment."""
    language: str
    runtime_version: str
    dependencies: List[str] = field(default_factory=list)
    databases: List[str] = field(default_factory=list)
    message_queues: List[str] = field(default_factory=list)
    external_services: List[str] = field(default_factory=list)
    generated_files: List[GeneratedFile] = field(default_factory=list)


class EnvironmentDetector:
    """Detect environment requirements from code."""

    def detect(self, code: str, language: str) -> EnvironmentMetadata:
        """Analyze code to detect environment requirements."""
        metadata = EnvironmentMetadata(
            language=language,
            runtime_version=self._get_default_runtime_version(language),
        )

        # Detect imports/dependencies
        metadata.dependencies = self._extract_dependencies(code, language)
        metadata.databases = self._extract_databases(code, language)
        metadata.message_queues = self._extract_message_queues(code, language)
        metadata.external_services = self._extract_external_services(code, language)

        return metadata

    def _get_default_runtime_version(self, language: str) -> str:
        """Get default runtime version for language."""
        defaults = {
            "python": "3.11",
            "javascript": "18",
            "typescript": "18",
            "go": "1.21",
            "rust": "1.73",
            "java": "21",
            "c#": "8.0",
            "ruby": "3.2",
            "php": "8.2",
        }
        return defaults.get(language, "latest")

    def _extract_dependencies(self, code: str, language: str) -> List[str]:
        """Extract package dependencies from code."""
        dependencies = []

        # Python
        if language == "python":
            if "import requests" in code or "from requests" in code:
                dependencies.append("requests")
            if "import flask" in code or "from flask" in code:
                dependencies.append("flask")
            if "import django" in code or "from django" in code:
                dependencies.append("django")
            if "import psycopg2" in code or "from psycopg2" in code:
                dependencies.append("psycopg2")
            if "import pymongo" in code or "from pymongo" in code:
                dependencies.append("pymongo")

        # JavaScript/Node.js
        elif language in ["javascript", "typescript"]:
            if "require('express')" in code or "from 'express'" in code:
                dependencies.append("express")
            if "require('axios')" in code or "from 'axios'" in code:
                dependencies.append("axios")
            if "require('pg')" in code or "from 'pg'" in code:
                dependencies.append("pg")
            if "require('mongoose')" in code or "from 'mongoose'" in code:
                dependencies.append("mongoose")

        # Go
        elif language == "go":
            if 'github.com/gin-gonic/gin' in code:
                dependencies.append("github.com/gin-gonic/gin")
            if 'github.com/lib/pq' in code:
                dependencies.append("github.com/lib/pq")
            if 'go.mongodb.org/mongo-driver' in code:
                dependencies.append("go.mongodb.org/mongo-driver")

        return dependencies

    def _extract_databases(self, code: str, language: str) -> List[str]:
        """Extract database requirements from code."""
        databases = []
        code_lower = code.lower()

        if "postgresql" in code_lower or "psycopg2" in code_lower:
            databases.append("postgresql")
        if "mysql" in code_lower or "pymysql" in code_lower:
            databases.append("mysql")
        if "mongodb" in code_lower or "pymongo" in code_lower:
            databases.append("mongodb")
        if "redis" in code_lower:
            databases.append("redis")
        if "sqlite" in code_lower:
            databases.append("sqlite")

        return databases

    def _extract_message_queues(self, code: str, language: str) -> List[str]:
        """Extract message queue requirements."""
        queues = []
        code_lower = code.lower()

        if "rabbitmq" in code_lower or "pika" in code_lower:
            queues.append("rabbitmq")
        if "kafka" in code_lower:
            queues.append("kafka")
        if "sqs" in code_lower or "boto3" in code_lower:
            queues.append("aws-sqs")

        return queues

    def _extract_external_services(self, code: str, language: str) -> List[str]:
        """Extract external service calls."""
        services = []
        code_lower = code.lower()

        if "api.github.com" in code_lower:
            services.append("github-api")
        if "api.stripe.com" in code_lower:
            services.append("stripe")
        if "api.twilio.com" in code_lower:
            services.append("twilio")
        if "aws.amazon.com" in code_lower or "boto3" in code_lower:
            services.append("aws")

        return services


class EnvironmentBuilder:
    """Build environment-specific files and infrastructure."""

    def __init__(self):
        self.detector = EnvironmentDetector()

    def build_environment(
        self,
        translated_code: str,
        target_language: str,
        output_dir: str,
        include_docker: bool = True,
        include_ci_cd: bool = True,
        cloud_provider: Optional[str] = None,
    ) -> EnvironmentMetadata:
        """Build complete environment for translated code."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Detect requirements
        metadata = self.detector.detect(translated_code, target_language)

        # Generate files based on target language and requirements
        generated_files = []

        # 1. Package manager files
        pkg_files = self._generate_package_files(target_language, metadata)
        generated_files.extend(pkg_files)

        # 2. Environment config files
        config_files = self._generate_config_files(target_language, metadata)
        generated_files.extend(config_files)

        # 3. Driver/interface files for detected services
        driver_files = self._generate_driver_files(target_language, metadata)
        generated_files.extend(driver_files)

        # 4. Docker files
        if include_docker:
            docker_files = self._generate_docker_files(target_language, metadata)
            generated_files.extend(docker_files)

        # 5. CI/CD pipelines
        if include_ci_cd:
            cicd_files = self._generate_cicd_files(target_language, metadata)
            generated_files.extend(cicd_files)

        # 6. Infrastructure as Code
        if cloud_provider:
            iac_files = self._generate_iac_files(target_language, metadata, cloud_provider)
            generated_files.extend(iac_files)

        # 7. Development setup
        dev_files = self._generate_dev_files(target_language, metadata)
        generated_files.extend(dev_files)

        # Write all files
        for gen_file in generated_files:
            file_path = output_path / gen_file.path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(gen_file.content, encoding="utf-8")

        metadata.generated_files = generated_files
        return metadata

    def _generate_package_files(self, language: str, metadata: EnvironmentMetadata) -> List[GeneratedFile]:
        """Generate package manager files."""
        files = []

        if language == "python":
            req_content = "\n".join(metadata.dependencies) if metadata.dependencies else "# No dependencies"
            files.append(GeneratedFile(
                path="requirements.txt",
                content=req_content,
                description="Python package dependencies",
                file_type="config",
            ))

        elif language in ["javascript", "typescript"]:
            pkg_json = {
                "name": "app",
                "version": "1.0.0",
                "description": "Auto-generated application",
                "main": "index.js",
                "dependencies": {dep: "latest" for dep in metadata.dependencies},
                "scripts": {
                    "start": "node index.js",
                    "dev": "nodemon index.js",
                },
            }
            files.append(GeneratedFile(
                path="package.json",
                content=json.dumps(pkg_json, indent=2),
                description="Node.js package manifest",
                file_type="config",
            ))

        elif language == "go":
            go_mod_content = f"""module app

go {metadata.runtime_version}

require (
"""
            for dep in metadata.dependencies:
                go_mod_content += f"    {dep}\n"
            go_mod_content += ")\n"

            files.append(GeneratedFile(
                path="go.mod",
                content=go_mod_content,
                description="Go module dependencies",
                file_type="config",
            ))

        elif language == "rust":
            cargo_toml = f"""[package]
name = "app"
version = "0.1.0"
edition = "2021"

[dependencies]
"""
            for dep in metadata.dependencies:
                cargo_toml += f"{dep} = \"*\"\n"

            files.append(GeneratedFile(
                path="Cargo.toml",
                content=cargo_toml,
                description="Rust package manifest",
                file_type="config",
            ))

        elif language == "java":
            pom_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>app</artifactId>
  <version>1.0.0</version>
  <dependencies>
"""
            for dep in metadata.dependencies:
                pom_xml += f"    <dependency>\n      <groupId>com.example</groupId>\n      <artifactId>{dep}</artifactId>\n    </dependency>\n"
            pom_xml += "  </dependencies>\n</project>\n"

            files.append(GeneratedFile(
                path="pom.xml",
                content=pom_xml,
                description="Maven project configuration",
                file_type="config",
            ))

        return files

    def _generate_config_files(self, language: str, metadata: EnvironmentMetadata) -> List[GeneratedFile]:
        """Generate configuration files."""
        files = []

        # .env template
        env_content = """# Application Configuration
DEBUG=false
PORT=5000
HOST=0.0.0.0

"""
        if "postgresql" in metadata.databases:
            env_content += """# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/app
"""
        if "redis" in metadata.databases:
            env_content += "REDIS_URL=redis://localhost:6379/0\n"
        if "mongodb" in metadata.databases:
            env_content += "MONGODB_URI=mongodb://localhost:27017/app\n"

        files.append(GeneratedFile(
            path=".env.example",
            content=env_content.strip(),
            description="Environment variables template",
            file_type="config",
        ))

        # .gitignore
        gitignore = """# Dependencies
node_modules/
venv/
.venv/
env/
target/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build
/build/
/dist/
*.o
*.so
"""
        files.append(GeneratedFile(
            path=".gitignore",
            content=gitignore.strip(),
            description="Git ignore rules",
            file_type="config",
        ))

        return files

    def _generate_driver_files(self, language: str, metadata: EnvironmentMetadata) -> List[GeneratedFile]:
        """Generate driver/interface files for detected services."""
        files = []

        # Database drivers
        if "postgresql" in metadata.databases:
            if language == "python":
                driver = """import psycopg2
from psycopg2 import sql

class PostgreSQLDriver:
    def __init__(self, connection_string):
        self.conn = psycopg2.connect(connection_string)
    
    def execute(self, query, params=None):
        cursor = self.conn.cursor()
        cursor.execute(query, params or ())
        self.conn.commit()
        return cursor.fetchall()
"""
                files.append(GeneratedFile(
                    path="drivers/postgresql.py",
                    content=driver,
                    description="PostgreSQL database driver",
                    file_type="driver",
                ))

        # Message queue drivers
        if "rabbitmq" in metadata.message_queues:
            if language == "python":
                driver = """import pika

class RabbitMQDriver:
    def __init__(self, host='localhost', port=5672):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, port=port)
        )
        self.channel = self.connection.channel()
    
    def publish(self, exchange, routing_key, message):
        self.channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message)
    
    def subscribe(self, queue, callback):
        self.channel.queue_declare(queue=queue, durable=True)
        self.channel.basic_consume(queue=queue, on_message_callback=callback)
        self.channel.start_consuming()
"""
                files.append(GeneratedFile(
                    path="drivers/rabbitmq.py",
                    content=driver,
                    description="RabbitMQ message queue driver",
                    file_type="driver",
                ))

        return files

    def _generate_docker_files(self, language: str, metadata: EnvironmentMetadata) -> List[GeneratedFile]:
        """Generate Docker files."""
        files = []

        # Determine base image
        base_images = {
            "python": f"python:{metadata.runtime_version}-slim",
            "javascript": f"node:{metadata.runtime_version}-alpine",
            "go": f"golang:{metadata.runtime_version}-alpine",
            "rust": f"rust:{metadata.runtime_version}",
            "java": f"openjdk:{metadata.runtime_version}-jdk-slim",
            "ruby": f"ruby:{metadata.runtime_version}-alpine",
            "php": f"php:{metadata.runtime_version}-fpm-alpine",
        }
        base_image = base_images.get(language, "ubuntu:22.04")

        # Dockerfile
        dockerfile = f"""FROM {base_image}
WORKDIR /app
COPY . .
"""

        if language == "python":
            dockerfile += "RUN pip install -r requirements.txt\nCMD [\"python\", \"app.py\"]\n"
        elif language in ["javascript", "typescript"]:
            dockerfile += "RUN npm install\nCMD [\"npm\", \"start\"]\n"
        elif language == "go":
            dockerfile += "RUN go build -o app\nCMD [\"./app\"]\n"
        elif language == "rust":
            dockerfile += "RUN cargo build --release\nCMD [\"./target/release/app\"]\n"

        dockerfile += "EXPOSE 5000\n"

        files.append(GeneratedFile(
            path="Dockerfile",
            content=dockerfile,
            description="Docker container definition",
            file_type="infrastructure",
        ))

        # docker-compose.yml
        services = {"app": {"build": ".", "ports": ["5000:5000"]}}

        if "postgresql" in metadata.databases:
            services["postgres"] = {
                "image": "postgres:15-alpine",
                "environment": {"POSTGRES_DB": "app"},
                "ports": ["5432:5432"],
            }

        if "redis" in metadata.databases:
            services["redis"] = {
                "image": "redis:7-alpine",
                "ports": ["6379:6379"],
            }

        if "mongodb" in metadata.databases:
            services["mongo"] = {
                "image": "mongo:6",
                "ports": ["27017:27017"],
            }

        docker_compose = f"""version: '3.8'

services:
"""
        for service_name, service_config in services.items():
            docker_compose += f"  {service_name}:\n"
            for key, value in service_config.items():
                if isinstance(value, dict):
                    docker_compose += f"    {key}:\n"
                    for k, v in value.items():
                        docker_compose += f"      {k}: {json.dumps(v)}\n"
                elif isinstance(value, list):
                    docker_compose += f"    {key}:\n"
                    for item in value:
                        docker_compose += f"      - {json.dumps(item)}\n"
                else:
                    docker_compose += f"    {key}: {json.dumps(value)}\n"

        files.append(GeneratedFile(
            path="docker-compose.yml",
            content=docker_compose,
            description="Docker Compose multi-service setup",
            file_type="infrastructure",
        ))

        # .dockerignore
        dockerignore = """node_modules
venv
.env
.git
.gitignore
README.md
.DS_Store
.vscode
.idea
"""
        files.append(GeneratedFile(
            path=".dockerignore",
            content=dockerignore.strip(),
            description="Docker build ignore rules",
            file_type="infrastructure",
        ))

        return files

    def _generate_cicd_files(self, language: str, metadata: EnvironmentMetadata) -> List[GeneratedFile]:
        """Generate CI/CD pipeline files."""
        files = []

        # GitHub Actions workflow
        github_workflow = f"""name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up {language}
        uses: actions/setup-{language}@v4
        with:
          {'python-version: ' + metadata.runtime_version if language == 'python' else 'node-version: ' + metadata.runtime_version if language in ['javascript', 'typescript'] else ''}
      - name: Install dependencies
        run: {'pip install -r requirements.txt' if language == 'python' else 'npm install' if language in ['javascript', 'typescript'] else 'go mod download'}
      - name: Run tests
        run: {'pytest' if language == 'python' else 'npm test' if language in ['javascript', 'typescript'] else 'go test ./...'}
  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t myapp:latest .
      - name: Push to registry
        run: docker push myapp:latest
"""
        files.append(GeneratedFile(
            path=".github/workflows/ci-cd.yml",
            content=github_workflow,
            description="GitHub Actions CI/CD pipeline",
            file_type="pipeline",
        ))

        return files

    def _generate_iac_files(self, language: str, metadata: EnvironmentMetadata, cloud_provider: str) -> List[GeneratedFile]:
        """Generate Infrastructure as Code files."""
        files = []

        if cloud_provider == "aws":
            # Terraform for AWS
            terraform = f"""terraform {{
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = "us-east-1"
}}

resource "aws_ecs_cluster" "main" {{
  name = "app-cluster"
}}

resource "aws_ecs_task_definition" "app" {{
  family                   = "app-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  
  container_definitions = jsonencode([{{
    name      = "app"
    image     = "my-registry/app:latest"
    essential = true
    portMappings = [{{
      containerPort = 5000
      hostPort      = 5000
      protocol      = "tcp"
    }}]
  }}])
}}
"""
            files.append(GeneratedFile(
                path="infrastructure/main.tf",
                content=terraform,
                description="Terraform AWS infrastructure",
                file_type="infrastructure",
            ))

        return files

    def _generate_dev_files(self, language: str, metadata: EnvironmentMetadata) -> List[GeneratedFile]:
        """Generate development setup files."""
        files = []

        # Makefile
        makefile = f"""# Development targets for {language}

.PHONY: help install test run build clean

help:
	@echo "Available targets:"
	@echo "  make install - Install dependencies"
	@echo "  make test    - Run tests"
	@echo "  make run     - Run application"
	@echo "  make build   - Build application"
	@echo "  make clean   - Clean build artifacts"

install:
"""
        if language == "python":
            makefile += "\tpip install -r requirements.txt\n"
        elif language in ["javascript", "typescript"]:
            makefile += "\tnpm install\n"
        elif language == "go":
            makefile += "\tgo mod download\n"
        elif language == "rust":
            makefile += "\tcargo fetch\n"

        makefile += "\ntest:\n"
        if language == "python":
            makefile += "\tpytest\n"
        elif language in ["javascript", "typescript"]:
            makefile += "\tnpm test\n"
        elif language == "go":
            makefile += "\tgo test ./...\n"
        elif language == "rust":
            makefile += "\tcargo test\n"

        makefile += "\nrun:\n"
        if language == "python":
            makefile += "\tpython app.py\n"
        elif language in ["javascript", "typescript"]:
            makefile += "\tnpm start\n"
        elif language == "go":
            makefile += "\tgo run main.go\n"
        elif language == "rust":
            makefile += "\tcargo run\n"

        makefile += "\nbuild:\n"
        if language == "python":
            makefile += "\tpyinstaller app.py\n"
        elif language in ["javascript", "typescript"]:
            makefile += "\tnpm run build\n"
        elif language == "go":
            makefile += "\tgo build -o app\n"
        elif language == "rust":
            makefile += "\tcargo build --release\n"

        makefile += "\nclean:\n\trm -rf build/ dist/ node_modules/ target/\n"

        files.append(GeneratedFile(
            path="Makefile",
            content=makefile,
            description="Development build targets",
            file_type="config",
        ))

        # README
        readme = f"""# Application

Auto-generated application for {language}.

## Setup

1. Install dependencies:
   ```bash
   make install
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Run the application:
   ```bash
   make run
   ```

## Development

- Run tests: `make test`
- Build for production: `make build`
- Clean build: `make clean`

## Docker

Build and run in Docker:
```bash
docker-compose up
```

## Requirements

"""
        if metadata.dependencies:
            readme += f"\nDependencies:\n"
            for dep in metadata.dependencies:
                readme += f"- {dep}\n"
        if metadata.databases:
            readme += f"\nDatabases:\n"
            for db in metadata.databases:
                readme += f"- {db}\n"

        files.append(GeneratedFile(
            path="README.md",
            content=readme.strip(),
            description="Project documentation",
            file_type="config",
        ))

        return files
