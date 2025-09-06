pipeline {
    agent any
    
    environment {
        // These will be set in Jenkins configuration
        OPENAI_API_KEY = credentials('openai-api-key')
        OPENROUTER_API_KEY = credentials('openrouter-api-key')
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '📥 Checking out code...'
                checkout scm
            }
        }
        
        stage('Build Images') {
            steps {
                echo '🏗️ Building Docker images...'
                script {
                    // Build backend image
                    bat 'docker build -t health-ai-backend ./backend'
                    
                    // Build frontend image  
                    bat 'docker build -t health-ai-frontend ./frontend'
                }
            }
        }
        
        stage('Test') {
            steps {
                echo '🧪 Running tests...'
                script {
                    // Stop any running containers
                    bat 'docker-compose down || exit 0'
                    
                    // Start test environment
                    bat 'docker-compose up -d'
                    
                    // Wait for services to be ready
                    bat 'timeout /t 30 /nobreak'
                    
                    // Test backend health
                    bat 'curl -f http://localhost:8000/health || exit 1'
                    
                    // Test frontend health  
                    bat 'curl -f http://localhost:8501 || exit 1'
                    
                    echo '✅ All health checks passed!'
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo '🚀 Deploying application...'
                script {
                    // Deploy to production (restart with latest images)
                    bat 'docker-compose down'
                    bat 'docker-compose up -d'
                    
                    echo '✅ Deployment complete!'
                    echo '🌐 Frontend: http://localhost:8501'
                    echo '📡 Backend API: http://localhost:8000'
                }
            }
        }
    }
    
    post {
        always {
            echo '🧹 Cleaning up...'
            // Clean up test containers but keep production running
            script {
                if (env.BRANCH_NAME != 'main') {
                    bat 'docker-compose down || exit 0'
                }
            }
        }
        success {
            echo '🎉 Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed. Check the logs above.'
        }
    }
}
