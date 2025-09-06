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
                    sh 'docker build -t health-ai-backend ./backend'
                    
                    // Build frontend image  
                    sh 'docker build -t health-ai-frontend ./frontend'
                }
            }
        }
        
        stage('Test') {
            steps {
                echo '🧪 Running tests...'
                script {
                    // Stop any running containers
                    sh 'docker-compose down || true'
                    
                    // Start test environment
                    sh 'docker-compose up -d'
                    
                    // Wait for services to be ready
                    sh 'sleep 30'
                    
                    // Test backend health
                    sh 'curl -f http://localhost:8000/health || exit 1'
                    
                    // Test frontend health  
                    sh 'curl -f http://localhost:8501 || exit 1'
                    
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
                    sh 'docker-compose down'
                    sh 'docker-compose up -d'
                    
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
                    sh 'docker-compose down || true'
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
